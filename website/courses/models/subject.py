from django.db import models
from django.utils.translation import gettext_lazy as _

from pytils.translit import slugify


class Subject(models.Model):
    """A model representing a subject."""

    title = models.CharField(_("title"), max_length=50,
                             help_text=_('Enter the subject title'))
    description = models.CharField(_("description"), max_length=50,
                                   help_text=_(
                                       'Enter a description of the subject'
                                   ))
    image = models.ImageField(_('image'), upload_to='subjects/images/',)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)

    class Meta:
        ordering = ['-title']
        verbose_name = _('subject')
        verbose_name_plural = _('subjects')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
