from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from courses.models.course import Course
from courses.models.lesson_progress import LessonProgress, LessonProgressEvent
from courses.models.lessons import Lesson
from courses.models.module import Module
from courses.models.subject import Subject
from courses.services.lesson_progress import (
    complete_step,
    course_progress,
    get_or_start_progress,
)


class LessonProgressServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='progress-service-user',
            email='progress-service-user@example.com',
        )
        subject = Subject.objects.create(
            title='Программирование',
            description='Тестовое направление',
            slug='service-programming',
            image='subjects/images/service.png',
        )
        self.course = Course.objects.create(
            owner=self.user,
            subject=subject,
            title='Курс сервисов',
            slug='service-course',
            description='Тестовый курс',
            image='courses/images/service.png',
            period=4,
            count_projects=1,
        )
        self.course.students.add(self.user)
        module = Module.objects.create(
            course=self.course,
            title='Модуль сервисов',
            description='Тестовый модуль',
            order=1,
        )
        self.lesson = Lesson.objects.create(
            module=module,
            title='Первый урок',
            order=1,
        )
        self.other_lesson = Lesson.objects.create(
            module=module,
            title='Второй урок',
            order=2,
        )

    def test_first_open_starts_progress_and_records_one_event(self):
        progress = get_or_start_progress(user=self.user, lesson=self.lesson)

        self.assertEqual(progress.status, LessonProgress.Status.IN_PROGRESS)
        self.assertIsNotNone(progress.started_at)
        self.assertIsNotNone(progress.last_opened_at)
        self.assertEqual(
            progress.events.filter(
                event_type=LessonProgressEvent.EventType.STARTED,
            ).count(),
            1,
        )

        get_or_start_progress(user=self.user, lesson=self.lesson)

        self.assertEqual(
            progress.events.filter(
                event_type=LessonProgressEvent.EventType.STARTED,
            ).count(),
            1,
        )

    def test_complete_step_advances_once_and_is_idempotent(self):
        get_or_start_progress(user=self.user, lesson=self.lesson)

        complete_step(user=self.user, lesson=self.lesson, step=1)
        complete_step(user=self.user, lesson=self.lesson, step=1)

        progress = LessonProgress.objects.get(
            user=self.user,
            lesson=self.lesson,
        )
        self.assertEqual(progress.current_step, 2)
        self.assertEqual(
            progress.events.filter(
                event_type=LessonProgressEvent.EventType.SECTION_COMPLETED,
                step=1,
            ).count(),
            1,
        )

    def test_forward_jump_is_rejected_without_changing_state(self):
        get_or_start_progress(user=self.user, lesson=self.lesson)

        with self.assertRaises(ValidationError):
            complete_step(user=self.user, lesson=self.lesson, step=3)

        progress = LessonProgress.objects.get(
            user=self.user,
            lesson=self.lesson,
        )
        self.assertEqual(progress.current_step, 1)
        self.assertFalse(progress.events.filter(step=3).exists())

    def test_fifth_step_completes_lesson_once(self):
        get_or_start_progress(user=self.user, lesson=self.lesson)

        for step in range(1, 6):
            complete_step(user=self.user, lesson=self.lesson, step=step)

        complete_step(user=self.user, lesson=self.lesson, step=5)
        progress = LessonProgress.objects.get(
            user=self.user,
            lesson=self.lesson,
        )
        self.assertEqual(progress.status, LessonProgress.Status.COMPLETED)
        self.assertEqual(progress.current_step, 5)
        self.assertIsNotNone(progress.completed_at)
        self.assertEqual(
            progress.events.filter(
                event_type=LessonProgressEvent.EventType.LESSON_COMPLETED,
            ).count(),
            1,
        )

    def test_reopening_completed_lesson_does_not_reset_it(self):
        get_or_start_progress(user=self.user, lesson=self.lesson)
        for step in range(1, 6):
            complete_step(user=self.user, lesson=self.lesson, step=step)

        get_or_start_progress(user=self.user, lesson=self.lesson)
        get_or_start_progress(user=self.user, lesson=self.lesson)

        progress = LessonProgress.objects.get(
            user=self.user,
            lesson=self.lesson,
        )
        self.assertEqual(progress.status, LessonProgress.Status.COMPLETED)
        self.assertEqual(progress.current_step, 5)
        self.assertEqual(
            progress.events.filter(
                event_type=LessonProgressEvent.EventType.REOPENED,
            ).count(),
            1,
        )

    def test_course_progress_counts_completed_lessons(self):
        get_or_start_progress(user=self.user, lesson=self.lesson)
        for step in range(1, 6):
            complete_step(user=self.user, lesson=self.lesson, step=step)

        result = course_progress(user=self.user, course=self.course)

        self.assertEqual(result['total_lessons'], 2)
        self.assertEqual(result['completed_lessons'], 1)
        self.assertEqual(result['percent'], 50)
        self.assertEqual(result['last_progress'].lesson, self.lesson)
