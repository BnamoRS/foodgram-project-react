# Generated by Django 3.2.15 on 2022-09-06 17:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0017_auto_20220905_1954'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='ingredients',
        ),
    ]
