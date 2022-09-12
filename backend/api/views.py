import re
from django.db.models import Count, Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import (
                                     ModelViewSet,
                                     ReadOnlyModelViewSet,
                                     )
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS
                                        )

from api import paginators, serializers
from api.filters import RecipeFilter
from api.permissions import IsAuthor
from recipes import models


def check_id(request, pk):
    id = request.data.get('id')
    if id is None or id != pk:
        return False
    return True


class UserViewSet(ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    pagination_class = paginators.CustomPageNumberPaginator
    permission_classes = [IsAuthenticatedOrReadOnly]

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
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        queryset = models.User.objects.filter(
            following__follower=request.user.id).prefetch_related(
                'recipes').annotate(
                    recipes_count=Count('recipes'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.SubscriptionSerializer(
                page,
                context={'request': request},
                many=True,
            )
            return self.get_paginated_response(serializer.data)
        serializer = serializers.SubscriptionSerializer(
                queryset,
                context={'request': request},
                many=True,
            )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk):
        if request.user.is_authenticated:
            if (
                models.Subscription.objects.filter(
                    author=pk, follower=self.request.user).exists()
            ):
                if request.method == 'DELETE':
                    models.Subscription.objects.filter(
                        author=pk, follower=self.request.user).delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(
                    {'errors': 'Подписка уже существует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif request.user.id == int(pk):
                return Response(
                    {'errors': 'Подписка на себя невозможна.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif models.User.objects.filter(id=pk).exists():
                author = models.User.objects.filter(id=pk).annotate(
                    recipes_count=Count('recipes')).first()
                models.Subscription.objects.create(
                    author=author, follower=self.request.user)
                serializer = serializers.SubscriptionSerializer(
                    author, context={'request': request})
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {'detail': 'Пользователь не существует.'},
                status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'detail': 'Пользователь не авторизован.'},
            status=status.HTTP_401_UNAUTHORIZED
            )


class TagViewSet(ReadOnlyModelViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewsSet(ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(ModelViewSet):
    queryset = models.Recipe.objects.prefetch_related(
        'recipe_ingredients__ingredient')
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = paginators.CustomPageNumberPaginator
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
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

    @action(
        methods=['post', 'delete'],
        detail=True,
        
        # permission_classes=[IsAuthenticated]
    )
    # перелопатить
    def favorite(self, request, pk):
        if request.user.is_authenticated:
            if (
                models.Favorite.objects.filter(
                    recipe=pk, user=self.request.user).exists()
            ):
                if request.method == 'DELETE':
                    models.Favorite.objects.filter(
                        recipe=pk, user=self.request.user).delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(
                    {'errors': 'Рецепт уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # elif request.user.id == int(pk):
            #     return Response(
            #         {'errors': 'Подписка на себя невозможна.'},
            #         status=status.HTTP_400_BAD_REQUEST
                # )
            if models.Recipe.objects.filter(id=pk).exists():
                recipe = models.Recipe.objects.get(id=pk)
                models.Favorite.objects.create(
                    recipe=recipe, user=self.request.user)
                serializer = serializers.FavoriteShoppingCartRecipeSerializer(
                    recipe, context={'request': request})
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {'detail': 'Рецепт не существует.'},
                status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'detail': 'Пользователь не авторизован.'},
            status=status.HTTP_401_UNAUTHORIZED
            )

        # if models.Recipe.objects.filter(id=pk).exists():
        #     if request.method == 'POST':
        #         serializer = serializers.FavoriteSerializer(
        #             data={'user': request.user.id, 'recipe': pk}
        #         )
        #         if serializer.is_valid():
        #             serializer.save()
        #             return Response(
        #                 serializer.data, status=status.HTTP_201_CREATED)
        #         return Response(
        #             serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #     if (
        #         not models.Favorite.objects.filter(
        #             user=request.user.id, recipe=pk).exists()
        #     ):
        #         return Response(
        #             {'errors': 'Рецепт отсутствует в подписке.'},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     models.Favorite.objects.filter(
        #         user=request.user, recipe=pk).delete()
        #     return Response(
        #         {'detail': 'Рецепт удалён из подписки.'},
        #         status=status.HTTP_204_NO_CONTENT,
        #     )
        # return Response(
        #         {'detail': 'Рецепт не найден.'},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        if request.user.is_authenticated:
            if (
                models.ShoppingCart.objects.filter(
                    recipe=pk, user=self.request.user).exists()
            ):
                if request.method == 'DELETE':
                    models.ShoppingCart.objects.filter(
                        recipe=pk, user=self.request.user).delete()
                    return Response(status=status.HTTP_204_NO_CONTENT)
                return Response(
                    {'errors': 'Рецепт уже в покупках.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            # elif request.user.id == int(pk):
            #     return Response(
            #         {'errors': 'Подписка на себя невозможна.'},
            #         status=status.HTTP_400_BAD_REQUEST
                # )
            if models.Recipe.objects.filter(id=pk).exists():
                recipe = models.Recipe.objects.get(id=pk)
                models.ShoppingCart.objects.create(
                    recipe=recipe, user=self.request.user)
                serializer = serializers.FavoriteShoppingCartRecipeSerializer(
                    recipe, context={'request': request})
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED)
            return Response(
                {'detail': 'Рецепт не существует.'},
                status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'detail': 'Пользователь не авторизован.'},
            status=status.HTTP_401_UNAUTHORIZED
            )

        # if check_id(request, pk):
        #     id_recipe = request.data.get('id')
        #     user = request.user
        #     if request.method == 'POST':
        #         serializer = serializers.ShoppingCartSerializer(
        #             data={'user': user.id, 'recipe': id_recipe}
        #         )
        #         if serializer.is_valid():
        #             serializer.save()
        #             return Response(
        #                 serializer.data, status=status.HTTP_201_CREATED)
        #         return Response(
        #             serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        #     if (
        #         not models.ShoppingCart.objects.filter(
        #             user=user.id, recipe=id_recipe).exists()
        #     ):
        #         return Response(
        #             {'errors': 'Рецепт отсутствует в списке покупок.'},
        #             status=status.HTTP_400_BAD_REQUEST,
        #         )
        #     models.ShoppingCart.objects.filter(
        #         user=user.id, recipe=id_recipe).delete()
        #     return Response(
        #         {'detail': 'Рецепт удалён из списка покупок.'},
        #         status=status.HTTP_204_NO_CONTENT,
        #     )
        # return Response(
        #         {'detail': 'Неверный id'},
        #         status=status.HTTP_404_NOT_FOUND
        # )

    @action(detail=False)
    def download_shopping_cart(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        user_id = request.user.id
        ingredients = models.Ingredient.objects.filter(
            recipe_ingredients__recipe_id__shopping_cart_recipes__user=user_id
        ).prefetch_related('recipe_ingredients').annotate(
            sum_amount=Sum('recipe_ingredients__amount'))
        serializer = serializers.ShoppingCartDownloadSerializer(
            ingredients, many=True)
        content = '***СПИСОК ПОКУПОК***\n\n'
        for val in serializer.data:
            content += '* {}: {} {}\n'.format(
                val['name'], val['amount'], val['measurement_unit'])
        return HttpResponse(
            content=content,
            content_type='text/plain'
        )
