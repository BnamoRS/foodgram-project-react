from dataclasses import field
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from recipes import models


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = models.User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return obj.follower.all().exists()


class UserCreateSerializer(ModelSerializer):
    
    class Meta:
        model = models.User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserListSerializer(ModelSerializer):

    class Meta:
        model = models.User
        fields = (
            
        )


# class UserMeSerializer(ModelSerializer):
#     model = models.User
#     fields = ('email', 'username', 'first_name', 'last_name',)
