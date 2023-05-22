from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

from .validators import validate_username
from core import texts
from core.enum import Limits


class User(AbstractUser):
    """Модель пользователя."""

    username = models.CharField(
        'Уникальный юзернейм',
        validators=(validate_username,),
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
        unique=True,
        blank=False,
        null=False,
        help_text=texts.USERS_HELP_UNAME,
        error_messages={'unique': texts.UNIQUE_USERNAME},
    )

    first_name = models.CharField(
        'Имя',
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
        blank=True,
        null=True,
        help_text=texts.USERS_HELP_FNAME,
    )

    last_name = models.CharField(
        'Фамилия',
        max_length=Limits.MAX_LEN_USERS_CHARFIELD.value,
        blank=True,
        null=True,
        help_text=texts.USERS_HELP_FNAME,
    )

    email = models.EmailField(
        'Электронная почта',
        max_length=Limits.MAX_LEN_EMAIL_FIELD.value,
        unique=True,
        blank=False,
        null=False,
        help_text=texts.USERS_HELP_EMAIL
    )

    birthdate = models.DateField(
        'Дата рождения',
        blank=True,
        null=True,
    )

    avatar = models.ImageField('Изображение',
                               help_text=texts.USER_AVATAR,
                               upload_to='accounts/images/',
                               blank=True, null=True,)

    phone_number = models.CharField(
        'Номер телефона', validators=[
            RegexValidator(
                regex=r'^(\+7|8)\d{10}$',
                message="Проверьте корректно ли указан номер телефона"
            )
        ],
        blank=False,
        help_text='Укажите номер телефона для связи', max_length=12
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email',)

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_username_email',
            )
        ]

    def __str__(self):
        return f'{self.username}: {self.email}'
