from django.core.management import call_command
from django.test import TestCase

from courses.models.course import Course
from courses.models.lesson_block import LessonBlock
from courses.models.lesson_material import LessonMaterial
from courses.models.lesson_progress import LessonProgress


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

    def test_pilot_block_seed_is_published_and_idempotent(self):
        call_command('seed_ml_materials', verbosity=0)
        call_command('seed_ml_lesson_blocks', verbosity=0)
        call_command('seed_ml_lesson_blocks', verbosity=0)

        course = Course.objects.get(slug='ml-inzhener')
        lesson = course.modules.get(title='Python для ML').lessons.get(
            title='Python для анализа данных'
        )
        blocks = LessonBlock.objects.filter(lesson=lesson).order_by('position')

        self.assertEqual(blocks.count(), 5)
        self.assertEqual(
            list(blocks.values_list('type', flat=True)),
            ['theory', 'image', 'code_example', 'image', 'summary'],
        )
        self.assertTrue(all(block.published for block in blocks))
        self.assertEqual(blocks.filter(position=10).first().content['markdown'], lesson.material.theory)

    def test_remaining_python_module_block_seed_is_idempotent(self):
        call_command('seed_ml_materials', verbosity=0)
        call_command('seed_ml_lesson_blocks', verbosity=0)
        call_command('seed_ml_python_lesson_blocks', verbosity=0)
        call_command('seed_ml_python_lesson_blocks', verbosity=0)

        course = Course.objects.get(slug='ml-inzhener')
        module = course.modules.get(title='Python для ML')
        lessons = module.lessons.exclude(title='Python для анализа данных')
        self.assertEqual(lessons.count(), 3)
        self.assertEqual(
            LessonBlock.objects.filter(lesson__in=lessons).count(),
            9,
        )
        for lesson in lessons:
            self.assertEqual(
                list(lesson.blocks.order_by('position').values_list('type', flat=True)),
                ['theory', 'code_example', 'summary'],
            )

    def test_course_seed_preserves_lessons_blocks_materials_and_progress(self):
        call_command('seed_ml_materials', verbosity=0)
        call_command('seed_ml_lesson_blocks', verbosity=0)
        course = Course.objects.get(slug='ml-inzhener')
        lesson = course.modules.get(title='Python для ML').lessons.get(
            title='Python для анализа данных'
        )
        lesson_id = lesson.id
        LessonProgress.objects.create(
            user=course.owner,
            lesson=lesson,
            status=LessonProgress.Status.IN_PROGRESS,
            current_step=3,
        )

        call_command('seed_ml_course', verbosity=0)

        course.refresh_from_db()
        lesson.refresh_from_db()
        self.assertEqual(lesson.id, lesson_id)
        self.assertTrue(LessonMaterial.objects.filter(lesson=lesson).exists())
        self.assertEqual(LessonBlock.objects.filter(lesson=lesson).count(), 5)
        self.assertEqual(
            LessonProgress.objects.get(user=course.owner, lesson=lesson).current_step,
            3,
        )
