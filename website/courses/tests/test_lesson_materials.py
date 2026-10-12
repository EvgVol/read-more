from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from courses.models.course import Course
from courses.models.lesson_material import LessonMaterial
from courses.models.lessons import Lesson
from courses.models.module import Module
from courses.models.subject import Subject


class LessonMaterialModelTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='material-test', email='material-test@example.com'
        )
        subject = Subject.objects.create(
            title='Тестирование',
            description='Тестовое направление',
            slug='testirovanie',
            image='subjects/images/test.png',
        )
        course = Course.objects.create(
            owner=user,
            subject=subject,
            title='Тестовый курс',
            slug='testovyi-kurs',
            overview='Тестовый обзор',
            description='Тестовое описание курса',
            image='courses/images/test.png',
            period=1,
            count_projects=1,
        )
        module = Module.objects.create(
            course=course,
            title='Тестовый модуль',
            description='Тестовое описание модуля',
            order=1,
        )
        self.lesson = Lesson.objects.create(
            module=module,
            title='Тестовый урок',
            order=1,
        )

    def test_material_is_saved_for_one_lesson(self):
        material = LessonMaterial.objects.create(
            lesson=self.lesson,
            objectives='Цель урока',
            theory='Теория урока',
            practice='Практика урока',
            self_check='Вопросы урока',
            resources='https://docs.python.org/3/tutorial/',
        )

        self.assertEqual(material.lesson, self.lesson)
        self.assertEqual(self.lesson.material, material)

    def test_lesson_accepts_only_one_material(self):
        LessonMaterial.objects.create(lesson=self.lesson)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                LessonMaterial.objects.create(lesson=self.lesson)

    def test_material_is_deleted_with_lesson(self):
        material = LessonMaterial.objects.create(lesson=self.lesson)

        self.lesson.delete()

        self.assertFalse(LessonMaterial.objects.filter(pk=material.pk).exists())
