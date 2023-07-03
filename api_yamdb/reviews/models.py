from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    ]
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Адрес электронной почты'
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Роль'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    first_name = models.CharField(
        'имя',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        'фамилия',
        max_length=150,
        blank=True
    )

    @property
    def is_user(self):
        return self.role == self.USER

    @property
    def is_admin(self):
        return (self.role == self.ADMIN
                or self.is_superuser)

    @property
    def is_moderator(self):
        return (self.role == self.MODERATOR
                or self.is_staff
                or self.is_admin)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self) -> str:
        return self.username


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(null=True)
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles')

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(User,
                               verbose_name='Автор',
                               related_name='reviews',
                               on_delete=models.CASCADE,
                               )
    title = models.ForeignKey(Title,
                              verbose_name='Произведение',
                              related_name='reviews',
                              on_delete=models.CASCADE,
                              )
    text = models.TextField(verbose_name='Текст')
    score = models.IntegerField(verbose_name='Оценка',
                                validators=[
                                    MinValueValidator(1),
                                    MaxValueValidator(10)
                                ])
    pub_date = models.DateTimeField(verbose_name='Дата публикации',
                                    auto_now_add=True,
                                    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'),
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(Review,
                               verbose_name='Отзыв',
                               related_name='comments',
                               on_delete=models.CASCADE,
                               )
    author = models.ForeignKey(User,
                               verbose_name='Автор комментария',
                               related_name='comments',
                               on_delete=models.CASCADE,
                               )
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(verbose_name='Время комментария',
                                    auto_now_add=True,
                                    )

    def __str__(self):
        return self.text
