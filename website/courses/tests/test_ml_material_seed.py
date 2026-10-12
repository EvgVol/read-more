from django.core.management import call_command
from django.test import TestCase

from courses.models.course import Course
from courses.models.lesson_material import LessonMaterial


class MlMaterialSeedTests(TestCase):
    def setUp(self):
        call_command('seed_ml_course', verbosity=0)

    def test_seed_creates_complete_material_for_every_ml_lesson(self):
        call_command('seed_ml_materials', verbosity=0)

        course = Course.objects.get(slug='ml-inzhener')
        materials = LessonMaterial.objects.filter(lesson__module__course=course)

        self.assertEqual(materials.count(), 28)
        for material in materials:
            self.assertTrue(material.objectives.strip())
            self.assertTrue(material.theory.strip())
            self.assertTrue(material.practice.strip())
            self.assertTrue(material.self_check.strip())
            self.assertTrue(material.resources.strip())

    def test_seed_is_idempotent(self):
        call_command('seed_ml_materials', verbosity=0)
        call_command('seed_ml_materials', verbosity=0)

        course = Course.objects.get(slug='ml-inzhener')

        self.assertEqual(
            LessonMaterial.objects.filter(lesson__module__course=course).count(),
            28,
        )

    def test_each_theory_is_long_form_and_structured(self):
        call_command('seed_ml_materials', verbosity=0)

        course = Course.objects.get(slug='ml-inzhener')
        materials = LessonMaterial.objects.filter(lesson__module__course=course)

        for material in materials:
            words = material.theory.split()
            self.assertGreaterEqual(
                len(words),
                6000,
                msg=f'{material.lesson.title}: expected at least 6000 theory words',
            )
            self.assertLessEqual(
                len(words),
                10000,
                msg=f'{material.lesson.title}: expected no more than 10000 theory words',
            )
            for heading in (
                '## Интуиция',
                '## Базовые понятия',
                '## Пошаговый разбор',
                '## Практические примеры',
                '## Типичные ошибки',
                '## Связь с ML-инженерией',
                '## Итоги',
            ):
                self.assertIn(heading, material.theory)
