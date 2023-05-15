from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.contrib.auth import get_user_model


User = get_user_model()


class PublishManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    """Модель поста."""

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Черновик'
        PUBLISHED = 'PB', 'Опубликовано'

    title = models.CharField('Заголовок', max_length=250)
    slug = models.SlugField('Slug', max_length=50, unique=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts',
                               verbose_name='Автор')
    body = models.TextField('Контент')
    publish = models.DateTimeField('Опубликовано', default=timezone.now)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    update = models.DateTimeField('Дата изменения', auto_now=True)
    status = models.CharField('Статус',
                              max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)
    objects = models.Manager()
    published = PublishManager()

    class Meta:
        ordering = ['-publish']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.title
