from django.db import models
from django.utils.translation import gettext_lazy as _

from .course import Course
from ..fields import OrderField


class Module(models.Model):
    """A model representing a module."""

    course = models.ForeignKey(Course,
                               verbose_name=_("course"),
                               related_name='modules',
                               on_delete=models.CASCADE)
    title = models.CharField(_("title"), max_length=50,
                             help_text=_('Enter the module title'))
    description = models.TextField(_("description"), blank=True,
                                   help_text=_(
                                       'Enter a description of the module'
                                   ))
    order = OrderField(blank=True, for_fields=['course'])
    image = models.ImageField(_("image"), upload_to='module_images/',
                              blank=True, help_text=_('Upload a .webp image'))

    class Meta:
        ordering = ['order']
        verbose_name = _('module')
        verbose_name_plural = _('modules')

    def __str__(self):
        return f'{self.order}. {self.title}'
