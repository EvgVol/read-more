from django.db import models
from django.utils.translation import gettext_lazy as _

from .lessons import Lesson


class LessonMaterial(models.Model):
    """Structured technical material for one course lesson."""

    lesson = models.OneToOneField(
        Lesson,
        related_name='material',
        verbose_name=_('lesson'),
        on_delete=models.CASCADE,
    )
    objectives = models.TextField(_('learning objectives'), blank=True)
    theory = models.TextField(_('theory'), blank=True)
    practice = models.TextField(_('practice'), blank=True)
    self_check = models.TextField(_('self-check'), blank=True)
    resources = models.TextField(_('resources'), blank=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    class Meta:
        ordering = ['lesson__module__order', 'lesson__order']
        verbose_name = _('lesson material')
        verbose_name_plural = _('lesson materials')

    def __str__(self):
        return f'Material: {self.lesson.title}'
