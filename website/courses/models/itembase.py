from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


User = get_user_model()


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


class Text(ItemBase):
    """A model representing text content."""

    content = models.TextField(_('content'))


class File(ItemBase):
    """A model representing text content."""

    file = models.FileField(_('file'), upload_to='files')


class Image(ItemBase):
    """A model representing text content."""

    image = models.FileField(_('image'), upload_to='images')


class Video(ItemBase):
    """A model representing text content."""

    url = models.URLField(_('url'))
