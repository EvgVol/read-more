from django.db import models
from django.utils.translation import gettext_lazy as _

from .course import Course


class CourseAuditRun(models.Model):
    """Saved snapshot of one editor-initiated course audit."""

    course = models.ForeignKey(
        Course,
        related_name='audit_runs',
        on_delete=models.CASCADE,
    )
    passed = models.BooleanField(default=False)
    modules_count = models.PositiveIntegerField(default=0)
    lessons_count = models.PositiveIntegerField(default=0)
    published_questions_count = models.PositiveIntegerField(default=0)
    issues_count = models.PositiveIntegerField(default=0)
    report = models.JSONField(default=dict)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created', '-id']
        verbose_name = _('course audit run')
        verbose_name_plural = _('course audit runs')

    def __str__(self):
        return f'{self.course.title} — {self.created:%Y-%m-%d %H:%M}'
