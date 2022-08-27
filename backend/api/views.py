from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from rest_framework.permissions import IsAuthenticated

from api import serializers
from recipes import models


class UserViewSet(ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserCreateSerializer
        # elif self.action == 'list':
        #     pass

        return serializers.UserSerializer

    @action(detail=False, url_path='me', permission_classes=[IsAuthenticated])
    def get_me(self, request):
        me = models.User.objects.get(id=request.user)
        serializer = serializers.UserSerializer(me)
        return Response(serializer.data)
