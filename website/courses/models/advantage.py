from django.db import models
from django.utils.translation import gettext_lazy as _


class Advantage(models.Model):

    name = models.CharField(_("name"), max_length=100)
    image = models.ImageField(_("image"),
                              upload_to='courses/advantages/images/')

    class Meta:
        verbose_name = _("advantage")
        verbose_name_plural = _("advantages")

    def __str__(self):
        return self.name
