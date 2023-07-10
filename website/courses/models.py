from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from pytils.translit import slugify

from .fields import OrderField


User = get_user_model()


class Subject(models.Model):
    """A model representing a subject."""

    title = models.CharField(_("title"), max_length=50,
                             help_text=_('Enter the subject title'))
    description = models.CharField(_("description"), max_length=50,
                                   help_text=_(
                                       'Enter a description of the subject'
                                   ))
    image = models.ImageField(_('image'), upload_to='courses/images/',)
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

    def get_absolute_url(self):
        return reverse("courses:manage_course_list", args={self.slug})


class Course (models.Model):
    """A model representing a course."""

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
    """A model representing a module."""

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
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']
        verbose_name = _('module')
        verbose_name_plural = _('modules')

    def __str__(self):
        return f'{self.order}. {self.title}'


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
