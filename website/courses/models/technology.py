from django.db import models
from django.utils.translation import gettext_lazy as _


class Technology(models.Model):
    name = models.CharField(_("name"), max_length=50, unique=True)
    url = models.URLField('URL', max_length=2000)
    hints = models.TextField(_("hints"))

    class Meta:
        verbose_name = _('technology')
        verbose_name_plural = 'technologies'

    def __str__(self):
        return self.name
