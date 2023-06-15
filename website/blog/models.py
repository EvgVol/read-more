from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone
from django.urls import reverse
from django.conf import settings

from taggit.managers import TaggableManager
from pytils.translit import slugify


class Category(models.Model):
    """
    Model for categories of blog posts.
    
    Args:
        models (django.db.models.Model): Django model class.
    
    Attributes:
        name (str): Name of the category.
        slug (str): Slug for the category.
    
    Meta:
        ordering (list): Default ordering for the model.
        verbose_name (str): Singular display name of the model.
        verbose_name_plural (str): Plural display name of the model.
    
    Methods:
        __str__(self) -> str:
            Returns the name of the category.
        
        save(self, *args, **kwargs):
            Overrides the save method to auto-generate slug.
        
        get_absolute_url(self) -> str:
            Returns the URL for the post list with this category.
    """

    name = models.CharField('Название', max_length=50)
    slug = models.SlugField('Slug', unique=True)

    class Meta:
        ordering = ['-name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        """
        Returns the name of the category.
        
        Returns:
            str: Name of the category.
        """
        return self.name

    def save(self, *args, **kwargs):
        """
        Overrides the save method to auto-generate slug.
        
        Args:
            *args: Positional arguments for the save method.
            **kwargs: Keyword arguments for the save method.
        """
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """
        Returns the URL for the post list with this category.
        
        Returns:
            str: URL for the post list with this category.
        """
        return reverse('blog:post_list_by_category', args=[self.slug])
    

class PublishManager(models.Manager):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    """Модель поста."""

    class Status(models.TextChoices):
        DRAFT = 'DF', 'Черновик'
        PUBLISHED = 'PB', 'Опубликовано'

    title = models.CharField('Заголовок', max_length=250)
    slug = models.SlugField('Slug', max_length=50,
                            unique_for_date='publish')
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
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
                              default=Status.PUBLISHED)
    objects = models.Manager()
    published = PublishManager()
    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        verbose_name='Понравилось',
                                        related_name='posts_liked',
                                        blank=True)

    class Meta:
        ordering = ['-publish']
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

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
