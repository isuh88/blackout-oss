from django.db.models import OuterRef, Exists
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from stores.models import Store, Prepay, UserPrepayRelease
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
