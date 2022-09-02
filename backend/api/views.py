from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import (ReadOnlyModelViewSet,
                                     ModelViewSet,
                                     GenericViewSet,
                                     )

from rest_framework.permissions import IsAuthenticated

from api import paginators, serializers
from api.viewsets import CreateDestroyListViewSet
from recipes import models


User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    pagination_class = paginators.UserPaginator

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserCreateSerializer
        return serializers.UserSerializer

    @action(detail=False, url_path='me', permission_classes=[IsAuthenticated])
    def get_me(self, request):
        me = models.User.objects.get(username=request.user)
        serializer = serializers.UserSerializer(me, context={'request': request})
        return Response(serializer.data)

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

    # @action(
    #     methods=['delete'],
    #     detail=True,
    #     url_path='subscribe',
    #     permission_classes=[IsAuthenticated]
    # )
    # def delete_subscribe(self, request, pk):
    #     pass


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
