# Generated by Django 3.2.15 on 2022-09-02 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_auto_20220902_2042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveIntegerField(verbose_name='количество'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipe', verbose_name='Рецепт'),
        ),
    ]
