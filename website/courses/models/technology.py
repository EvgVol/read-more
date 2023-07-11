from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

from courses.validators.uploadimage import validate_svg_image


class Technology(models.Model):

    name = models.CharField(_("name"), max_length=100)
    image = models.ImageField(_("image"),
                              upload_to='courses/technologies/images/',
                              validators=[
                                  FileExtensionValidator(
                                      allowed_extensions=['svg']
                                  ), validate_svg_image
                              ])

    class Meta:
        verbose_name = _("technology")
        verbose_name_plural = _("technologies")

    def __str__(self):
        return self.name
