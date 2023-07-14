from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.constants import (
    MAX_LEN_NAME,
    MAX_LEN_SLUG,
    MAX_SCORE,
    MIN_SCORE,)
from users.models import User
from users.validators import current_year


class Category(models.Model):
    """Модель категорий."""

    name = models.CharField('Категория', max_length=MAX_LEN_NAME)
    slug = models.SlugField(max_length=MAX_LEN_SLUG, unique=True)

    class Meta:
        ordering = ('slug',)

    def __str__(self):
        return f"{self.name} {self.slug}"


class Genre(models.Model):
    """Модель жанров."""

    name = models.CharField('Жанр', max_length=MAX_LEN_NAME)
    slug = models.SlugField(max_length=MAX_LEN_SLUG, unique=True)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return f"{self.name} {self.slug}"


class Title(models.Model):
    """Модель произведений."""

    name = models.CharField('Произведение', max_length=MAX_LEN_NAME)
    year = models.PositiveSmallIntegerField(
        'Год',
        blank=True,
        validators=[MaxValueValidator(limit_value=current_year)],)
    description = models.TextField('Описание', blank=True)
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        blank=True,
        null=True,)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.slug


class Review(models.Model):
    """Модель отзывов."""

    author = models.ForeignKey(User, on_delete=models.CASCADE,)
    title = models.ForeignKey(Title, on_delete=models.CASCADE,)
    text = models.TextField('Текст отзыва')
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(limit_value=MIN_SCORE),
            MaxValueValidator(limit_value=MAX_SCORE)],)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
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
        'Дата добавления', auto_now_add=True,)

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return self.text
