from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from pytils.translit import slugify

from .subject import Subject
from .technology import Technology


User = get_user_model()


class Course(models.Model):
    """A model representing a course."""

    class Complexity(models.TextChoices):
        """Choices for the complexity of the course"""

        JUNIOR = 'JN', _('junior')
        MIDDLE = 'MD', _('middle')
        SENIOR = 'SN', _('senior')

    owner = models.ForeignKey(User,
                              verbose_name=_("owner"),
                              related_name='courses_created',
                              on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject,
                                verbose_name=_("subject"),
                                related_name='courses',
                                on_delete=models.CASCADE)
    complexity = models.CharField(_('complexity'),
                                  max_length=2,
                                  choices=Complexity.choices,
                                  default=Complexity.JUNIOR)
    description = models.TextField(_("description"), max_length=650,
                                   help_text=_('Enter a description'))
    technologies = models.ManyToManyField(Technology,
                                          verbose_name=_("technologies"),
                                          related_name='courses')
    title = models.CharField(_("title"), max_length=200,
                             help_text=_('Enter the course title'))
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    overview = models.CharField(_("overview"), max_length=100)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    image = models.ImageField(_('image'), upload_to='courses/images/',)

    class Meta:
        ordering = ['created']
        verbose_name = _('course')
        verbose_name_plural = _('courses')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("courses:course_detail", kwargs={"pk": self.pk})

    def get_complexity_full_name(self):
        return dict(Course.Complexity.choices)[self.complexity]