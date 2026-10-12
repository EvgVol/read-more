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
