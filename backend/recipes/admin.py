from django.contrib import admin

from recipes import models


class RecipeTagInLine(admin.TabularInline):
    model = models.RecipeTag
    extra = 1


class IngredientInLine(admin.TabularInline):
    model = models.RecipeIngredient
    extra = 1
    list_display = ('ingredient', 'amount')
    search_fields = ('name',)


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeTagInLine, IngredientInLine)
    list_display = (
        'id', 'name', 'text', 'author', 'cooking_time', 'pub_date'
    )
    list_editable = (
        'name', 'text', 'author', 'cooking_time',
    )
    search_field = ('name', 'tag', 'author')
    list_filter = ('author', 'name', 'tags__name')
    empty_value_display = '--пусто--'


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    inlines = (RecipeTagInLine,)
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name',)
    list_editable = ('name', 'color', 'slug')


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    inlines = (IngredientInLine,)
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('follower', 'author')
