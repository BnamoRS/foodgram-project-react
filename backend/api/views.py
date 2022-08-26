from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from api import serializers
from recipes import models


class UserViewSet(ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
