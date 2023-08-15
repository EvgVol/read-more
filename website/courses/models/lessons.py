from django.db import models
from django.utils.translation import gettext_lazy as _

from .module import Module
from ..fields import OrderField


class Lesson(models.Model):

    module = models.ForeignKey(Module, verbose_name=_("module"),
                               on_delete=models.CASCADE)
    title = models.CharField(_("title"), max_length=50,
                             help_text=_('Enter the lesson title'))
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']
        verbose_name = _("lesson")
        verbose_name_plural = _("lessons")

    def __str__(self):
        return self.title
