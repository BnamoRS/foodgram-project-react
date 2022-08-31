from django.urls import include, path
from rest_framework.authtoken import views
from rest_framework.routers import DefaultRouter

from api.views import (
    SubscriptionViewSet, UserViewSet, TagViewSet, IngredientViewsSet)


appname = 'api'

router = DefaultRouter()

router.register(
    'users/subscriptions', SubscriptionViewSet, basename='subscriptions')
router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewsSet, basename='ingredients')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
