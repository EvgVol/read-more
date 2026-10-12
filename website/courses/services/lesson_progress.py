from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from courses.models.course import Course
from courses.models.lesson_progress import LessonProgress, LessonProgressEvent
from courses.models.lessons import Lesson


def get_or_start_progress(*, user, lesson: Lesson) -> LessonProgress:
    """Return a user's progress, creating or opening it when necessary."""
    now = timezone.now()
    with transaction.atomic():
        progress, created = LessonProgress.objects.select_for_update().get_or_create(
            user=user,
            lesson=lesson,
            defaults={
                'status': LessonProgress.Status.IN_PROGRESS,
                'current_step': 1,
                'started_at': now,
                'last_opened_at': now,
            },
        )
        if created:
            LessonProgressEvent.objects.create(
                progress=progress,
                event_type=LessonProgressEvent.EventType.STARTED,
            )
            return progress

        if progress.status == LessonProgress.Status.NOT_STARTED:
            progress.status = LessonProgress.Status.IN_PROGRESS
            progress.started_at = progress.started_at or now
            LessonProgressEvent.objects.create(
                progress=progress,
                event_type=LessonProgressEvent.EventType.STARTED,
            )
        elif progress.status == LessonProgress.Status.COMPLETED:
            previous_event = progress.events.first()
            if not previous_event or previous_event.event_type != LessonProgressEvent.EventType.REOPENED:
                LessonProgressEvent.objects.create(
                    progress=progress,
                    event_type=LessonProgressEvent.EventType.REOPENED,
                    step=progress.current_step,
                )

        progress.last_opened_at = now
        progress.save(update_fields=['status', 'started_at', 'last_opened_at', 'updated'])
        return progress


def complete_step(*, user, lesson: Lesson, step: int) -> LessonProgress:
    """Complete one sequential step without allowing forward jumps."""
    if step not in range(1, 6):
        raise ValidationError('Шаг урока должен быть от 1 до 5.')

    with transaction.atomic():
        progress = get_or_start_progress(user=user, lesson=lesson)
        progress = LessonProgress.objects.select_for_update().get(pk=progress.pk)

        if progress.status == LessonProgress.Status.COMPLETED:
            return progress
        if step > progress.current_step:
            raise ValidationError('Сначала завершите предыдущий этап урока.')
        if progress.events.filter(
            event_type=LessonProgressEvent.EventType.SECTION_COMPLETED,
            step=step,
        ).exists():
            return progress

        LessonProgressEvent.objects.create(
            progress=progress,
            event_type=LessonProgressEvent.EventType.SECTION_COMPLETED,
            step=step,
        )
        if step == 5:
            progress.status = LessonProgress.Status.COMPLETED
            progress.current_step = 5
            progress.completed_at = timezone.now()
            LessonProgressEvent.objects.create(
                progress=progress,
                event_type=LessonProgressEvent.EventType.LESSON_COMPLETED,
                step=5,
            )
        else:
            progress.status = LessonProgress.Status.IN_PROGRESS
            progress.current_step = step + 1
        progress.save(update_fields=[
            'status', 'current_step', 'completed_at', 'updated',
        ])
        return progress


def course_progress(*, user, course: Course) -> dict:
    """Return aggregate progress for a user in one course."""
    total_lessons = Lesson.objects.filter(module__course=course).count()
    completed_lessons = LessonProgress.objects.filter(
        user=user,
        lesson__module__course=course,
        status=LessonProgress.Status.COMPLETED,
    ).count()
    last_progress = LessonProgress.objects.filter(
        user=user,
        lesson__module__course=course,
    ).select_related('lesson', 'lesson__module').first()
    percent = round(completed_lessons * 100 / total_lessons) if total_lessons else 0
    return {
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'percent': percent,
        'last_progress': last_progress,
    }
