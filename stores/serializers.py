from django.db.models import F
from rest_framework import serializers

from stores.models import Store, Prepay, UserPrepayRelease


class PrepaySerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = Prepay
        fields = ['username', 'credit']

    def get_username(self, obj: Prepay):
        return obj.user.username


class PublicStoreSerializer(serializers.ModelSerializer):
    public_prepay = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = '__all__'

    def get_public_prepay(self, obj: Store):
        return obj.prepay_set.filter(type=Prepay.PrepayType.PUBLIC).annotate(username=F("user__username")).values('id', 'username', 'credit')


class PrivateStoreSerializer(serializers.ModelSerializer):
    private_prepay = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = '__all__'

    def get_private_prepay(self, obj: Store):
        return obj.prepay_set.filter(type=Prepay.PrepayType.PRIVATE).annotate(username=F("user__username")).values('id', 'username', 'credit')


class MyStoreSerializer(serializers.ModelSerializer):
    my_prepay = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = '__all__'

    def get_my_prepay(self, obj: Store):
        user = self.context['request'].user
        my_prepay_ids = UserPrepayRelease.objects.filter(user=user).values_list('prepay_id', flat=True)
        return Prepay.objects.filter(id__in=my_prepay_ids, store=obj).annotate(username=F("user__username")).values('id', 'username', 'credit')
