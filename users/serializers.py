from django.db.models import Sum, F
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from stores.models import UserPrepayRelease, Prepay
from users.models import User


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError('User with this username already exists.')
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserSigninSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class NestedPrepaySerializer(serializers.ModelSerializer):
    store_name = serializers.SerializerMethodField()

    class Meta:
        model = Prepay
        fields = ['id', 'store_name', 'credit']

    def get_store_name(self, obj: Prepay):
        return obj.store.name


class UserRetrieveSerializer(serializers.ModelSerializer):
    total_credits = serializers.SerializerMethodField()
    my_prepay = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'total_credits', 'my_prepay']

    def get_total_credits(self, obj: User):
        return obj.prepay_set.aggregate(total_credits=Sum('credit'))['total_credits'] or 0

    def get_my_prepay(self, obj: User):
        return NestedPrepaySerializer(obj.prepay_set.all(), many=True).data
