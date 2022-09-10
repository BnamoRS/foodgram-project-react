import base64

from django.core.files.base import ContentFile
from rest_framework.serializers import (
                                        Serializer,
                                        ModelSerializer,
                                        SerializerMethodField,
                                        CharField,
                                        ListField,
                                        ImageField,
                                        IntegerField,
                                        )
from rest_framework import exceptions

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

    def to_representation(self, instance):
        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return super().to_representation(instance)
        representation = super().to_representation(instance)
        representation.pop('is_subscribed')
        return representation

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return obj.following.filter(follower=request_user).exists()
        return False


class SetPasswordSerializer(ModelSerializer):
    current_password = CharField(style={"input_type": "password"})
    new_password = CharField(style={"input_type": "password"})

    class Meta:
        model = models.User
        fields = ('current_password', 'new_password')
        write_only_fields = ('current_password', 'new_password')

    def update(self, instance, validated_data):
        current_password = validated_data.get('current_password')
        new_password = validated_data.get('new_password')
        if not instance.check_password(current_password):
            raise exceptions.AuthenticationFailed(
                detail='Старый пароль не совпадает.')
        instance.set_password(new_password)
        instance.save()
        return instance


class UserCreateSerializer(ModelSerializer):
    password = CharField(style={"input_type": "password"}, write_only=True)

    def create(self, validated_data):
        instance = models.User.objects.create_user(**validated_data)
        return instance

    class Meta:
        model = models.User
        fields = (
            'email',
            'id',
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


class IngredientCreateRecipeSerializer(Serializer):
    amount = IntegerField()
    id = IntegerField()


class RecipeIngredientSerializer(ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = models.RecipeIngredient
        fields = ('amount', 'ingredient')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        ingredient = representation.pop('ingredient')
        amount = representation.pop('amount')
        ingredient['amount'] = amount
        return ingredient


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', many=True)
    image = Base64ImageField(required=False, allow_null=True)
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return models.Favorite.objects.filter(
                user=request_user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return models.ShoppingCart.objects.filter(
                user=request_user, recipe=obj).exists()

    def to_representation(self, instance):
        if self.context.get('request').user.is_authenticated:
            return super().to_representation(instance)
        representation = super().to_representation(instance)
        representation.pop('is_favorited')
        representation.pop('is_in_shopping_cart')
        return representation


class RecipeSubscriptionSerializer(ModelSerializer):
    # ingredients = RecipeIngredientSerializer(
    #     source='recipe_ingredients', many=True)
    # image = Base64ImageField(required=False, allow_null=True)
    # tags = TagSerializer(many=True)
    # author = UserSerializer(read_only=True)
    # is_favorited = SerializerMethodField()
    # is_in_shopping_cart = SerializerMethodField()

    class Meta:
        model = models.Recipe
        fields = (
            'id',
            # 'tags',
            # 'author',
            # 'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            # 'text',
            'cooking_time',
        )


class SubscriptionSerializer(ModelSerializer):
    recipes_count = IntegerField()
    recipes = RecipeSubscriptionSerializer(many=True)
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
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, obj):
        return UserSerializer.get_is_subscribed(self, obj)


class FavoriteShoppingCartRecipeSerializer(ModelSerializer):

    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.save()
        for ingredient in ingredients:
            id_ingredient = ingredient.get('id')
            if not models.Ingredient.objects.filter(id=id_ingredient).exists():
                raise exceptions.ParseError(detail='Игредиент не найден.')
            elif (
                not models.RecipeIngredient.objects.filter(
                    ingredient=id_ingredient, recipe=instance.id).exists()
            ):
                ingredient_obj = models.Ingredient.objects.get(
                    id=id_ingredient)
                amount_ingredient = ingredient.get('amount')
                models.RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient_obj,
                    amount=amount_ingredient,
                )
        for tag in tags:
            if not models.Tag.objects.filter(id=tag).exists():
                raise exceptions.ParseError(detail='Тег не найден.')
            elif (
                not models.RecipeTag.objects.filter(
                    recipe=instance, tag=tag).exists()
            ):
                current_tag = models.Tag.objects.get(id=tag)
                models.RecipeTag.objects.create(
                    recipe=instance, tag=current_tag)
        return instance


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

    def to_representation(self, instance):
        representation = FavoriteShoppingCartRecipeSerializer(instance.recipe)
        return representation.data


class ShoppingCartSerializer(ModelSerializer):

    class Meta:
        model = models.ShoppingCart
        fields = ('user', 'recipe')

    def create(self, validated_data):
        user = validated_data['user']
        recipe = validated_data['recipe']
        if (
            models.ShoppingCart.objects.filter(
                user=user, recipe=recipe).exists()
        ):
            raise exceptions.ParseError(
                detail='Рецепт уже добавлен в список покупок.')
        favorite = models.ShoppingCart.objects.create(
            user=user,
            recipe=recipe)
        return favorite

    def to_representation(self, instance):
        representation = FavoriteShoppingCartRecipeSerializer(instance.recipe)
        return representation.data


class ShoppingCartDownloadSerializer(ModelSerializer):
    amount = IntegerField(source='sum_amount')

    class Meta:
        model = models.Ingredient
        fields = ('name', 'amount', 'measurement_unit')
