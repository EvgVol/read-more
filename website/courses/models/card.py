from django.db import models
from django.utils.translation import gettext_lazy as _

from .course import Course


class Card(models.Model):

    title = models.CharField(_("title"), max_length=100)
    course = models.ForeignKey(Course,
                               verbose_name=_("course"),
                               on_delete=models.CASCADE,
                               related_name='courses')
    additional_text = models.TextField(_("additional text"))
    status = models.CharField(_("status"), max_length=10, blank=True)

    class Meta:
        verbose_name = _("card")
        verbose_name_plural = _("cards")

    def __str__(self):
        return self.title
