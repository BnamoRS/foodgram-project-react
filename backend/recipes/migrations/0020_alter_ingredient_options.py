# Generated by Django 3.2.15 on 2022-09-06 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0019_recipe_ingredients'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={'ordering': ['id'], 'verbose_name': 'Ингредиент', 'verbose_name_plural': 'Ингредиенты'},
        ),
    ]
