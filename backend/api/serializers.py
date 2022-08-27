from rest_framework.serializers import ModelSerializer

from recipes import models


class UserSerializer(ModelSerializer):

    class Meta:
        model = models.User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')


class UserMeSerializer(ModelSerializer):
    model = models.User
    fields = ('email', 'username', 'first_name', 'last_name',)
