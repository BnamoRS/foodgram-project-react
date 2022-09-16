import base64

from django.core.files.base import ContentFile
from rest_framework import exceptions
from rest_framework.serializers import (
                                        CharField,
                                        ImageField,
                                        IntegerField,
                                        ListField,
                                        ModelSerializer,
                                        Serializer,
                                        SerializerMethodField,
                                        )

from recipes.models import (
                            Favorite,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            RecipeTag,
                            ShoppingCart,
                            Tag,
                            User,
                            )


class UserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
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
        model = User
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

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        instance = User.objects.create_user(**validated_data)
        return instance


class TagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientCreateRecipeSerializer(Serializer):
    amount = IntegerField()
    id = IntegerField()


class RecipeIngredientSerializer(ModelSerializer):
    ingredient = IngredientSerializer(read_only=True)

    class Meta:
        model = RecipeIngredient
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
        model = Recipe
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

    def _get_is_in_model(self, obj, model):
        request_user = self.context.get('request').user
        if request_user.is_authenticated:
            return model.objects.filter(
                user=request_user, recipe=obj).exists()

    def get_is_favorited(self, obj):
        return self._get_is_in_model(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self._get_is_in_model(obj, ShoppingCart)

    def to_representation(self, instance):
        if self.context.get('request').user.is_authenticated:
            return super().to_representation(instance)
        representation = super().to_representation(instance)
        representation.pop('is_favorited')
        representation.pop('is_in_shopping_cart')
        return representation


class RecipeSubscriptionSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionSerializer(ModelSerializer):
    recipes_count = IntegerField()
    recipes = RecipeSubscriptionSerializer(many=True)
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipes_limit = self.context.get('request').query_params.get(
            'recipes_limit')
        if recipes_limit is None:
            return representation
        recipes = representation.pop('recipes')
        representation['recipes'] = recipes[:int(recipes_limit)]
        return representation


class FavoriteShoppingCartRecipeSerializer(ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeCreateUpdateSerializer(ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    tags = ListField(child=IntegerField(),)
    ingredients = IngredientCreateRecipeSerializer(
        many=True)

    class Meta:
        model = Recipe
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

    def _add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            id_ingredient = ingredient.get('id')
            if not Ingredient.objects.filter(id=id_ingredient).exists():
                raise exceptions.ParseError(detail='Игредиент не найден.')
            elif (
                not RecipeIngredient.objects.filter(
                    ingredient=id_ingredient, recipe=recipe.id).exists()
            ):
                ingredient_obj = Ingredient.objects.get(
                    id=id_ingredient)
                amount_ingredient = ingredient.get('amount')
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient_obj,
                    amount=amount_ingredient,
                )

    def _add_tags(self, tags, recipe):
        for tag in tags:
            if not Tag.objects.filter(id=tag).exists():
                raise exceptions.ParseError(detail='Тег не найден.')
            elif (
                not RecipeTag.objects.filter(
                    recipe=recipe, tag=tag).exists()
            ):
                current_tag = Tag.objects.get(id=tag)
                RecipeTag.objects.create(
                    recipe=recipe, tag=current_tag)

    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data, author=author)
        self._add_ingredients(ingredients, recipe)
        self._add_tags(tags, recipe)
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
        RecipeIngredient.objects.filter(recipe=instance.id).delete()
        self._add_ingredients(ingredients, instance)
        RecipeTag.objects.filter(recipe=instance).delete()
        self._add_tags(tags, instance)
        return instance


class ShoppingCartDownloadSerializer(ModelSerializer):
    amount = IntegerField(source='sum_amount')

    class Meta:
        model = Ingredient
        fields = ('name', 'amount', 'measurement_unit')
