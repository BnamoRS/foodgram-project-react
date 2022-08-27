from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Recipe(models.Model):
    """Рецепты."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    name = models.CharField(
        max_length=64,
        verbose_name='Название рецепта',
    )
    image = models.ImageField(verbose_name='Фото рецепта')
    description = models.TextField(
        max_length=200,
        verbose_name='Описание рецепта',
    )
    # как реализовать выбор из предустановленных для поля
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name=' Ингридиенты',
    )
    cooking_time = models.TimeField(verbose_name='Время приготовления, мин')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    tag = models.ManyToManyField(
        'Tag',
        through='RecipeTag',
        verbose_name='Тег',
    )


class Tag(models.Model):
    """Теги рецептов."""
    COLOR_TAG = [
        ('RED', '#cd5c5c'),
        ('BLUE', '#0000ff'),
        ('GREEN', '#008000'),
    ]
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=32) 
    # посмотреть как добавить цвет тега в HEX64
    # с цветами создать переменную выбора, в поле выбор из вариантов
    # в переменной цвет и его код.
    slug = models.SlugField(max_length=64)


class Ingredient(models.Model):
    """Таблица ингридиентов."""
    # UNITS = [
        
    # ]
    name = models.CharField(
        max_length=64,
        unique=True,
    )
    measurement_unit = models.CharField(
        max_length=2,
        # choices=UNITS
    )

    def add_unit(self, unit):
        """Добавить единицу измерения в список выбора."""
        # добавить единицу измерения написать
        pass


class RecipeIngredient(models.Model):
    """Таблица связи рецептов с ингридиентами."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT, # решить как удалять
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
    )
    amount = models.PositiveIntegerField()
    # сделать уникальным в пределах таблицы

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_recipe_ingredients'
            )
        ]


class RecipeTag(models.Model):
    """Таблица связи рецептов и тегов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.SET_NULL,
        related_name='recipe_tags',
        blank=True,
        null=True,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipe_tags'
    )


class Subscription(models.Model):
    """Подписка на пользователя."""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта'
    )
    # Подписку сделать уникальной для пары пользователей


class Favorite(models.Model):
    """Избранные рецепты."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )
    # сделать связку пользователь рецепт уникальной
