import base64
from dataclasses import field
from urllib import request

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.serializers import (
                                        ModelSerializer,
                                        SerializerMethodField,
                                        CharField,
                                        PrimaryKeyRelatedField,
                                        StringRelatedField,
                                        ImageField,
                                        IntegerField,
                                        )


from recipes import models
User = get_user_model()


# class BaseUserSerializer(ModelSerializer):

#     class Meta:
#         model = models.User
#         fields = (
#             'email',
#             'username',
#             'first_name',
#             'last_name',
#         )


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
        # print(self)
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


class RecipeIngredientSerializer(ModelSerializer):
    id = IntegerField()

    class Meta:
        model = models.RecipeIngredient
        fields = ('id', 'amount')

    # def get_alternate_name(self, obj):
    #     return obj.ingredient


class RecipeTagSerializer(ModelSerializer):
    # tag = TagSerializer(many=True)

    class Meta:
        model = models.RecipeTag
        fields = ('tag',)


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = RecipeIngredientSerializer(
        many=True)
    # tags = TagSerializer(many=True)

    class Meta:
        model = models.Recipe
        fields = (
            'ingredients',
            # 'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        author = self.context.get('request').user
        print(validated_data)
        ingredients = validated_data.pop('ingredients')
        print(ingredients)
        # tags = validated_data.pop('tags')
        # print(tags)
        recipe = models.Recipe.objects.create(**validated_data, author=author)
        for ingredient in ingredients:
            # current_ingredient = models.Ingredient.objects.get_or_create(
            #     **ingredient
            # )
            id_ingredient = ingredient.get('id')
            print(id_ingredient)
            ingredient_obj = get_object_or_404(models.Ingredient, id=id_ingredient)
            print(ingredient_obj)
            amount_ingredient = ingredient.get('amount')
            print(type(amount_ingredient))
            # Вставить проверку на наличие ингредиента в базе
            aaa = models.RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_obj,
                amount=amount_ingredient,
            )
            print(aaa)
        # for tag in tags:
        #     current_tag = models.Tag.objects.get_or_create(
        #         **tag
        #     )
        #     models.RecipeTag.objects.create(
        #         recipe=recipe, tag=current_tag
        #     )
        return recipe
