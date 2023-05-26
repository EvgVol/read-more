from django.db import models
from django.conf import settings
from pytils.translit import slugify


class Image(models.Model):
    """Модель изображений."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='images_created',
                             on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Slug', max_length=200, blank=True)
    url = models.URLField('URL', max_length=2000)
    image = models.ImageField('Изображение', 
                              upload_to='vookmarks/images/%Y/%m/%d/')
    description = models.TextField('Описание', blank=True)
    created = models.DateField('Дата создание', auto_now_add=True)
    users_like = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                        related_name='images_liked',
                                        verbose_name='Понравилось',
                                        blank=True)

    class Meta:
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'
        indexes = [
            models.Index(fields=['-created']),
        ]
        ordering = ['-created']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)