from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.urls import reverse

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
        blank=True,
        help_text='Укажите номер телефона для связи', max_length=12
    )

    about_me = models.TextField('О себе', blank=True,
                                help_text='Укажите информацию о себе',)

    following = models.ManyToManyField('self',
                                       through='Contact',
                                       related_name='followers',
                                       symmetrical=False)

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
        return f'{self.username}'

    def get_absolute_url(self):
        return reverse('profile', args=[self.username])


class Profile(models.Model):
    """Модель профиля пользователя."""
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile')

    def __str__(self):
        return f'Профиль {self.user.username}'


class Contact(models.Model):
    """Модель взаимосвязи между пользователями."""

    user_from = models.ForeignKey(User,
                                  related_name='rel_from_set',
                                  on_delete=models.CASCADE)
    user_to = models.ForeignKey(User,
                                related_name='rel_to_set',
                                on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        indexes = [
            models.Index(fields=['-created']),
        ]
        ordering = ['-created']
        constraints = [
            models.UniqueConstraint(
                fields=['user_from', 'user_to'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~models.Q(user_to=models.F('user_from')),
                name='no_self_follow'
            )
        ]

    def __str__(self):
        return f'{self.user_from} подписался на {self.user_to}'
