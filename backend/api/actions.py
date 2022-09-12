from rest_framework import status
from rest_framework.response import Response

from api import serializers
from recipes import models


def post_delete_action(obj, request, id, model):
    if (
        model.objects.filter(
            recipe=id, user=obj.request.user).exists()
    ):
        if request.method == 'DELETE':
            model.objects.filter(
                recipe=id, user=obj.request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт уже добавлен.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    if models.Recipe.objects.filter(id=id).exists():
        recipe = models.Recipe.objects.get(id=id)
        model.objects.create(
            recipe=recipe, user=obj.request.user)
        serializer = serializers.FavoriteShoppingCartRecipeSerializer(
            recipe, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(
        {'detail': 'Рецепт не существует.'},
        status=status.HTTP_400_BAD_REQUEST
        )

            # elif request.user.id == int(id):
        #     return Response(
        #         {'errors': 'Подписка на себя невозможна.'},
        #         status=status.HTTP_400_BAD_REQUEST
            # )
