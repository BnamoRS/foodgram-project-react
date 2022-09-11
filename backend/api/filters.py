from django_filters import rest_framework as filters

from recipes import models


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=models.Tag.objects.all(),
    )

    class Meta:
        model = models.Recipe
        fields = (
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'author',
            'tags',
        )
