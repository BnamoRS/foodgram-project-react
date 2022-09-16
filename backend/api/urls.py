from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    RecipeViewSet,
    # SubscriptionViewSet,
    UserViewSet,
    TagViewSet,
    IngredientViewsSet
)


appname = 'api'

router = DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewsSet, basename='ingredients')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
