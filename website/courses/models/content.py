from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.utils.translation import gettext_lazy as _

from .module import Module
from ..fields import OrderField


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
