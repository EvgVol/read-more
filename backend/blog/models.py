from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse

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
    slug = models.SlugField('Slug', max_length=50, unique_for_date='publish')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='blog_posts',
                               verbose_name='Автор')
    body = models.TextField('Контент')
    image = models.ImageField('Изображение', upload_to='blog/images/',)
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
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail',
                       args=[self.publish.year,
                             self.publish.month,
                             self.publish.day,
                             self.slug])
