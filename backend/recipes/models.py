from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Recipe(models.Model):
    """Рецепты."""
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        verbose_name=' Ингридиенты',
        )
    tags = models.ManyToManyField(
        'Tag',
        through='RecipeTag',
        verbose_name='Тег',
        )
    image = models.ImageField(
        upload_to='recipe/images/',
        null=True,
        default=None,
        verbose_name='Фото рецепта',
        )
    name = models.CharField(
        unique=True,
        max_length=200,
        verbose_name='Название рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления, мин',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']


class Tag(models.Model):
    """Теги рецептов."""
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование тега',
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет в HEX',
        unique=True,
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Уникальный слаг',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Таблица ингридиентов."""
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Наименование ингридиента',
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения',
    )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id']


class RecipeIngredient(models.Model):
    """Таблица связи рецептов с ингридиентами."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='recipe_ingredients',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт',
    )
    amount = models.PositiveIntegerField(verbose_name='количество')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
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
        related_name='recipe_tags',
        verbose_name='Тег',
    )

    class Meta:
        verbose_name = 'Тег рецепта'
        verbose_name_plural = 'Теги рецепта'


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

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'author'],
                name='unique_subscription'
            )
        ]


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

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipes',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_users',
    )

    class Meta:
        verbose_name = 'Покупка'
        verbose_name_plural = 'Покупки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]
