from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import (ReadOnlyModelViewSet,
                                     ModelViewSet,
                                     )

from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS
                                        )

from api import paginators, serializers
from api.permissions import IsAuthor
from api.viewsets import CreateDestroyListViewSet
from recipes import models


User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    pagination_class = paginators.CustomPageNumberPaginator

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserCreateSerializer
        return serializers.UserSerializer

    @action(detail=False, url_path='me', permission_classes=[IsAuthenticated])
    def get_me(self, request):
        me = models.User.objects.get(username=request.user)
        serializer = serializers.UserSerializer(
            me, context={'request': request})
        return Response(serializer.data)

    @action(
        methods=['post'],
        detail=False,
        url_path='set_password',
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = models.User.objects.get(username=request.user)
        self.check_object_permissions(request, user)
        serializer = serializers.SetPasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'detail': 'Пароль успешно изменен.'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='subscribe',
        permission_classes=[IsAuthenticated]
    )
    def add_subscribe(self, request, pk):
        if request.method == 'POST':
            author = get_object_or_404(User, id=pk)
            models.Subscription.objects.create(
                author=author, follower=self.request.user)
            serializer = serializers.UserSerializer(
                author, context={'request': request})
            return Response(serializer.data)
        models.Subscription.objects.filter(
            author=pk, follower=self.request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewsSet(ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class SubscriptionViewSet(CreateDestroyListViewSet):
    queryset = models.Subscription.objects.all()
    serializer_class = serializers.SubscriptionSerializer
    pagination_class = paginators.SubscriptionPaginator
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.follower.all()


class RecipeViewSet(ModelViewSet):
    queryset = models.Recipe.objects.prefetch_related(
        'recipe_ingredients__ingredient')
    # serializer_class = serializers.RecipeSerializer
    # pagination_class = None

    def get_serializer_class(self):
        # print(self.action)
        if self.action == 'list' or self.action == 'retrieve':
            return serializers.RecipeSerializer
        elif self.action == 'destroy':
            return serializers.RecipeDestroySerializer
        else:
            return serializers.RecipeCreateUpdateSerializer

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            permission_classes = [IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [IsAuthor]
        return [permission() for permission in permission_classes]

    def destroy(self, request, pk):
        serializer = serializers.RecipeDestroySerializer(
            data=request.data)
        print(request.data)
        if serializer.is_valid():
            recipe_id = serializer.validated_data.get('id')
            models.Recipe.objects.get(id=recipe_id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        # return super().destroy(request, *args, **kwargs)

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='favorite',
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        id_recipe = request.data.get('id')
        user = request.user
        if request.method == 'POST':
            serializer = serializers.FavoriteSerializer(
                data={'user': user.id, 'recipe': id_recipe}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if (
            not models.Favorite.objects.filter(
                user=user.id, recipe=id_recipe).exists()
        ):
            return Response(
                {'errors': 'Рецепт отсутствует в подписке.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        models.Favorite.objects.filter(user=user.id, recipe=id_recipe).delete()
        return Response(
            {'detail': 'Рецепт удалён из подписки.'},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        methods=['post', 'delete'],
        detail=True,
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        id_recipe = request.data.get('id')
        user = request.user
        if request.method == 'POST':
            serializer = serializers.ShoppingCartSerializer(
                data={'user': user.id, 'recipe': id_recipe}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if (
            not models.ShoppingCart.objects.filter(
                user=user.id, recipe=id_recipe).exists()
        ):
            return Response(
                {'errors': 'Рецепт отсутствует в списке покупок.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        models.ShoppingCart.objects.filter(
            user=user.id, recipe=id_recipe).delete()
        return Response(
            {'detail': 'Рецепт удалён из списка покупок.'},
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shoping_cart(self, request):
        ingredients = models.Ingredient.objects.filter(
            recipe_ingredients__recipe_id__shopping_cart_recipes__user=request.user.id
        ).prefetch_related('ingredients').annotate(
            amount=Sum('recipe_ingredients__amount'))
        recipes = models.Recipe.objects.filter(
            shopping_cart_recipes__user=request.user.id).prefetch_related(
                'recipe_ingredients__ingredient')
        # ingredients = models.Recipe.objects.filter(
        #     id__in=recipes)
        # ingredients_ingr = ingredients.recipe_ingredients.all()
        print(ingredients.values())
        serializer = serializers.RecipeSerializer(
            recipes, many=True, context={'request': request})
        return Response(serializer.data)
