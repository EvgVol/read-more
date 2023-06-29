from typing import Iterable, Optional
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from pytils.translit import slugify


User = get_user_model()


class Subject(models.Model):
    """Модель предмета."""

    title = models.CharField(_("title"), max_length=200,
                             help_text=_('Enter the subject title'))
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


class Course (models.Model):
    """Модель курса."""

    owner = models.ForeignKey(User,
                              verbose_name=_("owner"),
                              related_name='courses_created',
                              on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,
                                verbose_name=_("subject"),
                                related_name='courses',
                                on_delete=models.CASCADE)
    title = models.CharField(_("title"), max_length=200,
                             help_text=_('Enter the course title'))
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    overview = models.TextField(_("overview"))
    created = models.DateTimeField(_("created"), auto_now_add=True)

    class Meta:
        ordering = ['-created']
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Module (models.Model):
    """Модель модуля."""

    course = models.ForeignKey(Course,
                               verbose_name=_("course"),
                               related_name='modules',
                               on_delete=models.CASCADE)
    title = models.CharField(_("title"), max_length=200,
                             help_text=_('Enter the module title'))
    description = models.TextField(_("description"), blank=True,
                                   help_text=_(
                                       'Enter a description of the module'
                                   ))

    class Meta:
        ordering = ['-title']
        verbose_name = _('module')
        verbose_name_plural = _('modules')

    def __str__(self):
        return self.title


class Content(models.Model):
    """Модель контентента."""

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

    class Meta:
        verbose_name = _('content')
        verbose_name_plural = _('contents')


class ItemBase(models.Model):
    """Абстрактная модель содержание контента."""

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
    content = models.TextField(_('content'))


class File(ItemBase):
    file = models.FileField(_('file'), upload_to='files')


class Image(ItemBase):
    image = models.FileField(_('image'), upload_to='images')


class Video(ItemBase):
    url = models.URLField(_('url'))
