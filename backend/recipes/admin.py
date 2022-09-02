from django.contrib import admin

from recipes import models


class TagInLine(admin.TabularInline):
    model = models.RecipeTag
    extra = 1


class IngredientInLine(admin.TabularInline):
    model = models.RecipeIngredient
    extra = 1
    list_display = ('ingredient', 'amount')


class RecipeAdmin(admin.ModelAdmin):
    # model = models.Recipe
    inlines = (TagInLine, IngredientInLine)
    list_display = (
        'id', 'name', 'text', 'author', 'cooking_time', 'pub_date'
    )
    search_field = ('name', 'tag', 'author')
    list_filter = ('pub_date',)
    empty_value_display = '--пусто--'


class TagAdmin(admin.ModelAdmin):
    inlines = (TagInLine,)
    list_display = ('id', 'name', 'color', 'slug')


class IngredientAdmin(admin.ModelAdmin):
    # model = models.Ingredient
    inlines = (IngredientInLine,)
    list_display = ('id', 'name', 'measurement_unit')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('follower', 'author')


admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)
