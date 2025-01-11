from django.db.models import OuterRef, Exists
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from web3 import Web3

from stores.models import Store, Prepay, UserPrepayRelease
from users.models import User
from stores.serializers import PublicStoreSerializer, PrivateStoreSerializer, MyStoreSerializer


class PublicStoreListAPI(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = PublicStoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.annotate(
            is_public=Exists(Prepay.objects.filter(store_id=OuterRef("id"), type=Prepay.PrepayType.PUBLIC))
        ).filter(is_public=True)


class PrivateStoreListAPI(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = PrivateStoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.annotate(
            is_public=Exists(Prepay.objects.filter(store_id=OuterRef("id"), type=Prepay.PrepayType.PRIVATE))
        ).filter(is_public=True)


class MyStoreListAPI(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = MyStoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        my_prepay_ids = UserPrepayRelease.objects.filter(user=user).values_list('prepay_id', flat=True)
        store_ids = Prepay.objects.filter(id__in=my_prepay_ids).values_list('store_id', flat=True)

        return self.queryset.filter(id__in=store_ids)


class PrepayIsValidAPI(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        prepay_id = data.get('prepay_id')
        code = data.get('code')

        is_valid = Prepay.objects.filter(id=prepay_id, code=code).exists()
        return Response({'is_valid': is_valid})


class PrepayAddHookAPI(APIView):
    permission_classes = []  # 외부 웹훅 접근을 위해 인증 제외
    
    def decode_log_data(self, data: str):
        # ABI 타입 정의
        abi_types = [
            "string",      # store_name
            "address",     # signer
            "string",      # record_type
            "uint256",     # credit
            "uint256",     # new_total
            "address"      # store
        ]
        
        # web3 인스턴스 생성
        w3 = Web3()
        
        # 데이터 디코딩
        try:
            # 0x 제거 후 디코딩
            decoded = w3.codec.decode(abi_types, bytes.fromhex(data[2:]))
            
            # address 타입에 0x prefix 추가
            signer_address = f"{decoded[1]}"
            store_address = f"{decoded[5]}"
            
            return {
                'store_name': decoded[0],
                'signer': signer_address,
                'record_type': decoded[2],
                'credit': decoded[3],
                'new_total': decoded[4],
                'store_address': store_address
            }
        except Exception as e:
            raise ValueError(f"Failed to decode data: {str(e)}")
    
    def post(self, request):
        try:
            data = request.data
            
            # 웹훅 데이터 검증
            if not data.get('event') or not data['event'].get('messages'):
                raise ValueError("Invalid webhook data format")
            
            # 첫 번째 메시지의 데이터 추출
            message = data['event']['messages'][0]
            hex_data = message['data']
            
            # 데이터 디코딩
            decoded_data = self.decode_log_data(hex_data)
            
            # Store 조회 또는 생성
            store, store_created = Store.objects.get_or_create(
                name=decoded_data['store_name'],
                defaults={
                    'wallet_address': decoded_data['store_address'],
                    'address': 'seoul, korea'  # default 값 설정
                }
            )

            print(decoded_data['signer'])
            
            # User 조회
            try:
                user = User.objects.get(wallet_address=decoded_data['signer'])
            except User.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': f"User not found with wallet address: {decoded_data['signer']}"
                }, status=404)
            
            # Prepay 레코드 조회 또는 생성
            prepay, prepay_created = Prepay.objects.get_or_create(
                store=store,
                user=user,
                type=decoded_data['record_type'],
                defaults={
                    'credit': decoded_data['new_total']
                }
            )
            
            # 기존 레코드가 있었다면 credit 업데이트
            if not prepay_created:
                prepay.credit = decoded_data['new_total']
                prepay.save()
            
            return Response({
                'status': 'success',
                'message': 'Prepay data processed successfully',
                'decoded_data': decoded_data,
                'action': {
                    'store': 'created' if store_created else 'existing',
                    'prepay': 'created' if prepay_created else 'updated'
                }
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)


class PrepayUseHookAPI(APIView):
    permission_classes = []  # 외부 웹훅 접근을 위해 인증 제외
    
    def decode_log_data(self, data: str):
        # ABI 타입 정의
        abi_types = [
            "string",      # store_name
            "address",     # signer
            "string",      # record_type
            "uint256",     # credit
            "uint256"      # remaining
        ]
        
        # web3 인스턴스 생성
        w3 = Web3()
        
        # 데이터 디코딩
        try:
            # 0x 제거 후 디코딩
            decoded = w3.codec.decode(abi_types, bytes.fromhex(data[2:]))
            
            # address 타입에 0x prefix 추가
            signer_address = f"{decoded[1]}"
            
            return {
                'store_name': decoded[0],
                'signer': signer_address,
                'record_type': decoded[2],
                'credit': decoded[3],
                'remaining': decoded[4]
            }
        except Exception as e:
            raise ValueError(f"Failed to decode data: {str(e)}")
    
    def post(self, request):
        try:
            data = request.data
            
            # 웹훅 데이터 검증
            if not data.get('event') or not data['event'].get('messages'):
                raise ValueError("Invalid webhook data format")
            
            # 첫 번째 메시지의 데이터 추출
            message = data['event']['messages'][0]
            hex_data = message['data']
            
            # 데이터 디코딩
            decoded_data = self.decode_log_data(hex_data)
            
            # Store 조회
            try:
                store = Store.objects.get(name=decoded_data['store_name'])
            except Store.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Store not found'
                }, status=404)
            
            # Prepay 레코드 조회
            try:
                prepay = Prepay.objects.get(
                    store=store,
                    user__wallet_address=decoded_data['signer'],
                    type=decoded_data['record_type']
                )
            except Prepay.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Prepay record not found'
                }, status=404)
            
            # credit 업데이트
            prepay.credit = decoded_data['remaining']
            prepay.save()
            
            return Response({
                'status': 'success',
                'message': 'Prepay data processed successfully',
                'decoded_data': decoded_data
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=400)
