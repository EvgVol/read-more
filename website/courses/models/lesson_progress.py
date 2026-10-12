from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from .lessons import Lesson


User = get_user_model()


class LessonProgress(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = 'not_started', _('Не начат')
        IN_PROGRESS = 'in_progress', _('В процессе')
        COMPLETED = 'completed', _('Завершён')

    user = models.ForeignKey(
        User,
        related_name='lesson_progress',
        on_delete=models.CASCADE,
    )
    lesson = models.ForeignKey(
        Lesson,
        related_name='progress_records',
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NOT_STARTED,
    )
    current_step = models.PositiveSmallIntegerField(default=1)
    started_at = models.DateTimeField(null=True, blank=True)
    last_opened_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'lesson'],
                name='unique_lesson_progress_user_lesson',
            ),
            models.CheckConstraint(
                check=Q(current_step__gte=1) & Q(current_step__lte=5),
                name='lesson_progress_step_1_to_5',
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['lesson', 'status']),
        ]

    def __str__(self):
        return f'{self.user} — {self.lesson} — {self.get_status_display()}'


class LessonProgressEvent(models.Model):
    class EventType(models.TextChoices):
        STARTED = 'started', _('Урок начат')
        SECTION_COMPLETED = 'section_completed', _('Этап завершён')
        LESSON_COMPLETED = 'lesson_completed', _('Урок завершён')
        REOPENED = 'reopened', _('Урок открыт повторно')

    progress = models.ForeignKey(
        LessonProgress,
        related_name='events',
        on_delete=models.CASCADE,
    )
    event_type = models.CharField(max_length=24, choices=EventType.choices)
    step = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=Q(step__isnull=True) | (
                    Q(step__gte=1) & Q(step__lte=5)
                ),
                name='lesson_progress_event_step_1_to_5',
            ),
        ]
        indexes = [
            models.Index(fields=['progress', 'created_at']),
            models.Index(fields=['event_type', 'created_at']),
        ]

    def __str__(self):
        return f'{self.progress} — {self.get_event_type_display()}'
