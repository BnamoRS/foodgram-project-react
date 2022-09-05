import base64
from dataclasses import field
from urllib import request

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.serializers import (
                                        Serializer,
                                        ModelSerializer,
                                        SerializerMethodField,
                                        CharField,
                                        ListField,
                                        PrimaryKeyRelatedField,
                                        StringRelatedField,
                                        ImageField,
                                        IntegerField,
                                        RelatedField,
                                        )
from rest_framework import exceptions


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


# class IngredientAmountField(RelatedField):

#     def to_representation(self, value):
#         print(value.name)
#         return value


class IngredientSerializer(ModelSerializer):
    # recipe_ingredients = IngredientAmountField(many=False)

    # РЕШИТЬ ПРОБЛЕМУ С AMOUNT

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['amount'] = models.RecipeIngredient.objects.get(
    #         ingredient=instance).amount
    #     return representation

    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientCreateRecipeSerializer(Serializer):
    amount = IntegerField()
    id = IntegerField()

    # class Meta:
    #     # model = models.Ingredient
    #     fields = ('id', 'amount')


class SubscriptionSerializer(ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = models.Subscription
        fields = ('author',)


# class RecipeIngredientSerializer(ModelSerializer):
#     # ingredient = IngredientSerializer(read_only=True)

#     class Meta:
#         model = models.RecipeIngredient
#         fields = ('amount',)
        

#     # def get_alternate_name(self, obj):
#     #     return obj.ingredient


# class TagCreateRecipeSerializer(Serializer):
#     tags = IntegerField()
#     # class Meta:
#     #     model = models.RecipeTag
#     #     fields = ('tags',)


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = IngredientSerializer(
        many=True)
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    # def to_internal_value(self, data):
        
    #     print(data)
    #     return super().to_internal_value(data)

    # def to_representation(self, instance):
    #     return super().to_representation(instance)

    # def create(self, validated_data):
    #     print(validated_data)


class RecipeCreateUpdateSerializer(ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    tags = ListField(child=IntegerField(),)
    ingredients = IngredientCreateRecipeSerializer(
        many=True)

    class Meta:
        model = models.Recipe
        fields = (
            'ingredients',
            'tags',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def to_representation(self, instance):
        custom_request = self.context.get('request')
        representation = RecipeSerializer(
            instance, context={'request': custom_request})
        return representation.data

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = models.Recipe.objects.create(**validated_data, author=author)
        for ingredient in ingredients:
            id_ingredient = ingredient.get('id')
            if not models.Ingredient.objects.filter(id=id_ingredient).exists():
                raise exceptions.ParseError(detail='Игредиент не найден.')
            ingredient_obj = models.Ingredient.objects.get(id=id_ingredient)
            amount_ingredient = ingredient.get('amount')
            models.RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_obj,
                amount=amount_ingredient,
            )
        for tag in tags:
            if not models.Tag.objects.filter(id=tag).exists():
                raise exceptions.ParseError(detail='Тег не найден.')
            current_tag = models.Tag.objects.get(id=tag)
            models.RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        return recipe


class FavoriteSerializer(ModelSerializer):

    class Meta:
        model = models.Favorite
        fields = ('user', 'recipe')

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        if models.Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise exceptions.ParseError(detail='Рецепт уже в подписке.')
        favorite = models.Favorite.objects.create(
            user=user,
            recipe=recipe)
        return favorite
