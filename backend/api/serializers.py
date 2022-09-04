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
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['amount'] = models.RecipeIngredient.objects.get(
            ingredient=instance).amount
        return representation

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


class RecipeIngredientSerializer(ModelSerializer):
    # ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = models.RecipeIngredient
        fields = ('amount',)
        

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
    ingredients = IngredientSerializer(
        many=True)
    tags = TagSerializer(many=True)
    author = UserSerializer()

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


# class RecipeCreateUpdateSerializer(ModelSerializer):
#     image = Base64ImageField(required=False, allow_null=True)
#     # tags = PrimaryKeyRelatedField(
#     #     queryset=models.Tag.objects.all(), many=True)
#     ingredients = IngredientCreateRecipeSerializer(
#         many=True)
#     # is_favorited = SerializerMethodField()
#     # is_in_shoping_cart = SerializerMethodField()

#     class Meta:
#         model = models.Recipe
#         fields = (
#             # 'id',
#             # 'tags',
#             # 'author',
#             'ingredients',
#             # 'is_favorited',
#             # 'is_in_shopping_cart',
#             'name',
#             'image',
#             'text',
#             'cooking_time',
#         )
#         # read_only_fields = (
#         #     # 'id',
#         #     # 'author',
#         #     'is_favorited',
#         #     'is_in_shopping_cart',
#         # )

#     # def get_is_favorited(self, obj):
#     #     print(obj)
#     #     return True


#     def create(self, validated_data):
#         author = self.context.get('request').user
#     #     print(validated_data)
#         ingredients = validated_data.pop('ingredients')
#         print(ingredients)
#         # tags = validated_data.pop('tags')
#         # print(tags)
#         recipe = models.Recipe.objects.create(**validated_data, author=author)
#         for ingredient in ingredients:
#             # current_ingredient = models.Ingredient.objects.get_or_create(
#             #     **ingredient
#             # )
#             id_ingredient = ingredient.get('id')
#             print(id_ingredient)
#             # if not models.Ingredient.objects.filter(id=id_ingredient).exists():
#             #     raise exceptions.ParseError(detail='Игредиент не найден.')
#             ingredient_obj = get_object_or_404(models.Ingredient, id=id_ingredient)
#             print(ingredient_obj)
#             amount_ingredient = ingredient.get('amount')
#             print(type(amount_ingredient))
#             # Вставить проверку на наличие ингредиента в базе
#             recipe_ingredient = models.RecipeIngredient.objects.create(
#                 recipe=recipe,
#                 ingredient=ingredient_obj,
#                 amount=amount_ingredient,
#             )
#             print(recipe_ingredient)
#         # for tag in tags:
#         #     current_tag = models.Tag.objects.get_or_create(
#         #         **tag
#         #     )
#         #     models.RecipeTag.objects.create(
#         #         recipe=recipe, tag=current_tag
#         #     )
#         return recipe
