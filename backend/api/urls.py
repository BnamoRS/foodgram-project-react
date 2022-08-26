from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views


appname = 'api'

router = DefaultRouter()

router.register('user', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]