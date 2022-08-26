from rest_framework.serializers import ModelSerializer

from recipes import models


class UserSerializer(ModelSerializer):

    class Meta:
        model = models.User
        fields = '__all__'
