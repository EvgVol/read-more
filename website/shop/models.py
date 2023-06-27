from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from parler.models import TranslatableModel, TranslatedFields
from pytils.translit import slugify


class Category(TranslatableModel):
    """Модель категорий магазина."""

    translations = TranslatedFields(
        name = models.CharField(_('name'), max_length=50),
        slug = models.SlugField(_('slug'), max_length=50, unique=True)
    )

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class Product(models.Model):
    """Модель категорий товара."""

    translations = TranslatedFields(
        name = models.CharField(_('name'), max_length=200),
        slug = models.SlugField(_('slug'), max_length=200, unique=True),
        category = models.ForeignKey(Category,
                                    related_name='products',
                                    verbose_name=_('category'),
                                    on_delete=models.CASCADE),
        image = models.ImageField(_('image'),
                                upload_to='products/%Y/%m/%d',
                                blank=True),
        description = models.TextField(_('description'), blank=True),
        price = models.DecimalField(_('price'), max_digits=10,
                                    decimal_places=2),
        available = models.BooleanField(_('available'), default=True),
        created = models.DateTimeField(_('created'), auto_now_add=True),
        updated = models.DateTimeField(_('updated'), auto_now=True),
    )
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created']),
        ]
        verbose_name = _('product')
        verbose_name_plural = _('products')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail',
                       args=[self.category.slug,
                             self.slug])
