from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse

from taggit.managers import TaggableManager


User = get_user_model()


class Category(models.Model):
    """Модель категорий."""

    name = models.CharField('Название', max_length=50)
    slug = models.SlugField('Slug', unique=True)

    class Meta:
        ordering = ['-name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.name


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
    tags = TaggableManager()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, blank=False,
                                 related_name='posts',
                                 verbose_name='Категория')
    image = models.ImageField('Изображение', upload_to='blog/images/',)
    publish = models.DateTimeField('Опубликовано', default=timezone.now)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Дата изменения', auto_now=True)
    status = models.CharField('Статус',
                              max_length=2,
                              choices=Status.choices,
                              default=Status.DRAFT)
    objects = models.Manager()
    published = PublishManager()

    class Meta:
        ordering = ['-publish']
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
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


class Comment(models.Model):
    """Модель комментариев."""

    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             verbose_name='Статья')
    name = models.CharField('Имя отправителя', max_length=80)
    email = models.EmailField('Электронный адрес(email)')
    body = models.TextField('Комментарий')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True, verbose_name='Активный')

    class Meta:
        ordering = ['created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        indexes = [
            models.Index(fields=['created']),
        ]
    
    def __str__(self):
        return f'Комментарий от {self.name} к статье {self.post}'
