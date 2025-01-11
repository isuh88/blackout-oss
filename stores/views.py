from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from stores.models import Store
from stores.serializers import StoreSerializer


class PublicStoreListAPI(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(store_type=Store.StoreType.PUBLIC)


class PrivateStoreListAPI(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(store_type=Store.StoreType.PRIVATE)


class MyStoreListAPI(generics.ListAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(userstorerelease__user=self.request.user).prefetch_related("userstorerelease_set")

