from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .lessons import Lesson


class LessonBlock(models.Model):
    """Version-one content block kept alongside legacy LessonMaterial."""

    class Type(models.TextChoices):
        THEORY = 'theory', _('Theory')
        IMAGE = 'image', _('Image')
        SUMMARY = 'summary', _('Summary')
        CODE_EXAMPLE = 'code_example', _('Code example')

    lesson = models.ForeignKey(
        Lesson,
        related_name='blocks',
        verbose_name=_('lesson'),
        on_delete=models.CASCADE,
    )
    type = models.CharField(_('type'), max_length=32)
    position = models.PositiveIntegerField(_('position'), default=10)
    schema_version = models.PositiveSmallIntegerField(_('schema version'), default=1)
    content = models.JSONField(_('content'), default=dict, blank=True)
    config = models.JSONField(_('configuration'), default=dict, blank=True)
    published = models.BooleanField(_('published'), default=False)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    class Meta:
        ordering = ['position', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['lesson', 'position'],
                name='unique_lesson_block_position',
            ),
        ]
        indexes = [
            models.Index(fields=['lesson', 'published', 'position']),
        ]
        verbose_name = _('lesson block')
        verbose_name_plural = _('lesson blocks')

    def __str__(self):
        return f'{self.lesson} — {self.type} — {self.position}'

    def clean(self):
        super().clean()
        from courses.services.lesson_blocks import validate_lesson_block_payload

        validate_lesson_block_payload(
            block_type=self.type,
            content=self.content,
            config=self.config,
            schema_version=self.schema_version,
        )
