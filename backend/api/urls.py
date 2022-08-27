from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from api.views import UserViewSet


appname = 'api'

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/token/login', views.obtain_auth_token),
    path('', include(router.urls)),
]