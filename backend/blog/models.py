from django.db import models
from django.utils import timezone


class Post(models.Model):
    """Модель поста."""

    title = models.CharField('Заголовок', max_length=250)
    slug = models.SlugField('Slug', max_length=50)
    body = models.TextField('Контент')
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]

    def __str__(self):
        return self.title 
