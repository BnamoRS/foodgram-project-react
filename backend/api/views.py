from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api import serializers
from recipes import models


class UserViewSet(ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

    @action(methods=['get'], detail=True, url_path='me')
    def get_me(self, request):
        me = models.User.objects.get(id=request.user)
        serializer = serializers.UserMeSerializer(me)
        return Response(serializer.data)
