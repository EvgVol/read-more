from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

from .module import Module
from ..fields import OrderField


class ItemBase(models.Model):
    """An abstract base class for content items."""

    owner = models.ForeignKey(User,
                              verbose_name=_('owner'),
                              related_name='%(class)s_related',
                              on_delete=models.CASCADE)
    title = models.CharField(_('title'), max_length=250,
                             help_text=_('Enter a title'))
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Content(models.Model):
    """A model representing the content of a module."""

    module = models.ForeignKey(Module,
                               verbose_name=_('module'),
                               related_name='contents',
                               on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'),
                                     on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': ('text',
                                                                     'video',
                                                                     'image',
                                                                     'file')})
    object_id = models.PositiveIntegerField(_('object id'))
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']
        verbose_name = _('content')
        verbose_name_plural = _('contents')


class Text(ItemBase):
    """A model representing text content."""

    content = models.TextField(_('content'))


class File(ItemBase):
    """A model representing text content."""

    file = models.FileField(_('file'), upload_to='files')


class Image(ItemBase):
    """A model representing text content."""

    file = models.FileField(_('image'), upload_to='images')


class Video(ItemBase):
    """A model representing text content."""

    url = models.URLField(_('url'))
