from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import User
from .serializers import UserSignupSerializer, UserSigninSerializer


class UserSignupAPI(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        token = Token.objects.create(user=user)
        headers = self.get_success_headers(serializer.data)
        response = {
            'user': {
                'username': user.username,
                'token': token.key,
            }
        }
        return Response(response, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()


class UserSigninAPI(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSigninSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(username=serializer.validated_data["username"], password=serializer.validated_data["password"])
        if not user:
            return Response(
                data={"message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            data={"token": token.key},
            status=status.HTTP_200_OK,
        )


class UserRetrieveAPI(generics.GenericAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)
