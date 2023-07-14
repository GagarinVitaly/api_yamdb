from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.constants import (
    MAX_LEN_NAME,
    MAX_LEN_SLUG,
    MAX_SCORE,
    MIN_SCORE, )
from users.models import User


class Category(models.Model):
    """Модель категорий."""

    name = models.CharField('Категория', max_length=MAX_LEN_NAME)
    slug = models.SlugField(max_length=MAX_LEN_SLUG, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('slug',)

    def __str__(self):
        return f"{self.name} {self.slug}"


class Genre(models.Model):
    """Модель жанров."""

    name = models.CharField('Жанр', max_length=MAX_LEN_NAME)
    slug = models.SlugField(max_length=MAX_LEN_SLUG, unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('id',)

    def __str__(self):
        return f"{self.name} {self.slug}"


class Title(models.Model):
    """Модель произведений."""

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Категория',
        related_name='titles'
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    name = models.CharField('Произведение', max_length=MAX_LEN_NAME)
    year = models.IntegerField(verbose_name='Год выпуска', )
    description = models.TextField('Описание', blank=True, null=True)

    class Meta:
        ordering = ('id',)
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Вспомогательная модель для произведений."""

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)


class Review(models.Model):
    """Модель отзывов."""

    author = models.ForeignKey(User, on_delete=models.CASCADE, )
    title = models.ForeignKey(Title, on_delete=models.CASCADE, )
    text = models.TextField('Текст отзыва')
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(limit_value=MIN_SCORE),
            MaxValueValidator(limit_value=MAX_SCORE)], )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Обзор'
        verbose_name_plural = 'Обзоры'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title')]

    def __str__(self):
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария')
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарии')
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('id',)

    def __str__(self):
        return self.text
