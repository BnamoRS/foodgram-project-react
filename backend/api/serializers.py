from django.contrib.auth import get_user_model
from rest_framework.serializers import (
                                        ModelSerializer,
                                        SerializerMethodField,
                                        CharField,
                                        StringRelatedField
                                        )


from recipes import models
User = get_user_model()

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
        # print(obj)
        request_user = self.context.get('request').user
        # print(request_user)
        return obj.following.filter(follower=request_user).exists()


class UserCreateSerializer(ModelSerializer):
    password = CharField(style={"input_type": "password"}, write_only=True)

    def create(self, validated_data):
        instance = models.User.objects.create_user(**validated_data)
        return instance
    
    class Meta:
        model = models.User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class TagSerializer(ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')


class SubscriptionSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = models.Subscription
        fields = ('author',)
