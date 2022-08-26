from django.contrib import admin

from recipes import models


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'author', 'cooking_time', 'pub_date',
    )
    search_field = ('name', 'tag', 'author')
    list_filter = ('pub_date',)
    empty_value_display = '--пусто--'


admin.site.register(models.Recipe, RecipeAdmin)
