from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from courses.models.course import Course
from courses.models.lessons import Lesson
from courses.models.module import Module
from courses.models.lesson_progress import LessonProgress, LessonProgressEvent
from courses.models.subject import Subject


class LessonProgressModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='progress-model-user',
            email='progress-model-user@example.com',
        )
        subject = Subject.objects.create(
            title='Программирование',
            description='Тестовое направление',
            slug='progress-programming',
            image='subjects/images/progress.png',
        )
        course = Course.objects.create(
            owner=self.user,
            subject=subject,
            title='Курс прогресса',
            slug='progress-course',
            description='Тестовый курс',
            image='courses/images/progress.png',
            period=4,
            count_projects=1,
        )
        module = Module.objects.create(
            course=course,
            title='Модуль прогресса',
            description='Тестовый модуль',
            order=1,
        )
        self.lesson = Lesson.objects.create(
            module=module,
            title='Урок прогресса',
            order=1,
        )

    def test_progress_has_beginner_friendly_defaults(self):
        progress = LessonProgress.objects.create(
            user=self.user,
            lesson=self.lesson,
        )

        self.assertEqual(progress.status, LessonProgress.Status.NOT_STARTED)
        self.assertEqual(progress.current_step, 1)
        self.assertIsNone(progress.started_at)
        self.assertIsNone(progress.last_opened_at)
        self.assertIsNone(progress.completed_at)

    def test_progress_is_unique_per_user_and_lesson(self):
        LessonProgress.objects.create(user=self.user, lesson=self.lesson)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                LessonProgress.objects.create(
                    user=self.user,
                    lesson=self.lesson,
                )

    def test_progress_event_is_deleted_with_progress(self):
        progress = LessonProgress.objects.create(
            user=self.user,
            lesson=self.lesson,
        )
        LessonProgressEvent.objects.create(
            progress=progress,
            event_type=LessonProgressEvent.EventType.STARTED,
        )

        progress.delete()

        self.assertFalse(LessonProgressEvent.objects.exists())

    def test_invalid_step_is_rejected_by_database_constraint(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                LessonProgress.objects.create(
                    user=self.user,
                    lesson=self.lesson,
                    current_step=6,
                )
