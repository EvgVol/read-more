from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .lessons import Lesson


class QuizQuestion(models.Model):
    class Type(models.TextChoices):
        SINGLE = 'single', _('Один вариант')
        MULTIPLE = 'multiple', _('Несколько вариантов')
        SHORT = 'short', _('Короткий ответ')

    lesson = models.ForeignKey(
        Lesson,
        related_name='quiz_questions',
        on_delete=models.CASCADE,
    )
    type = models.CharField(max_length=16, choices=Type.choices)
    position = models.PositiveIntegerField(default=10)
    prompt = models.TextField()
    options = models.JSONField(default=list, blank=True)
    correct_answers = models.JSONField(default=list, blank=True)
    explanation = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    points = models.PositiveIntegerField(default=1)
    published = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['lesson', 'position'],
                name='unique_quiz_question_position',
            ),
        ]

    def __str__(self):
        return f'{self.lesson} — {self.position}'


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='quiz_attempts',
        on_delete=models.CASCADE,
    )
    lesson = models.ForeignKey(
        Lesson,
        related_name='quiz_attempts',
        on_delete=models.CASCADE,
    )
    earned_points = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_points = models.PositiveIntegerField(default=0)
    passed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at', '-id']
        indexes = [
            models.Index(fields=['user', 'lesson', 'submitted_at']),
        ]

    @property
    def percent(self):
        if not self.total_points:
            return 0
        return round(float(self.earned_points) / self.total_points * 100)


class QuizAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        related_name='answers',
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(
        QuizQuestion,
        related_name='attempt_answers',
        on_delete=models.CASCADE,
    )
    selected_answers = models.JSONField(default=list, blank=True)
    normalized_answer = models.TextField(blank=True)
    awarded_points = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_correct = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['attempt', 'question'],
                name='unique_quiz_answer_question',
            ),
        ]
