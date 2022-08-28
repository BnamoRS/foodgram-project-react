import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Команда для загрузки списка ингредиентов в базу данных'

    def handle(self, *args, **options):
        with open('ingredients.json') as file:
            ingredients = json.load(file)
        for ingredient in ingredients:
            name = ingredient.get('name')
            measurement_unit = ingredient.get('measurement_unit')
            if not Ingredient.objects.filter(name=name).exists():
                Ingredient.objects.create(
                    name=name, measurement_unit=measurement_unit)
