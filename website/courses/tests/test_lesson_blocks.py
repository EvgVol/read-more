from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from courses.models.course import Course
from courses.models.lesson_block import LessonBlock
from courses.models.lesson_material import LessonMaterial
from courses.models.lessons import Lesson
from courses.models.module import Module
from courses.models.subject import Subject
from courses.services.lesson_blocks import (
    get_lesson_stage_content,
    render_lesson_blocks,
)


class LessonBlockTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='blocks-user', email='blocks-user@example.com'
        )
        subject = Subject.objects.create(
            title='Программирование',
            description='Тестовое направление',
            slug='blocks-programming',
            image='subjects/images/blocks.png',
        )
        course = Course.objects.create(
            owner=self.user,
            subject=subject,
            title='Курс блоков',
            slug='blocks-course',
            description='Тестовый курс',
            image='courses/images/blocks.png',
            period=1,
            count_projects=1,
        )
        module = Module.objects.create(
            course=course,
            title='Модуль блоков',
            description='Тестовый модуль',
            order=1,
        )
        self.lesson = Lesson.objects.create(
            module=module,
            title='Урок блоков',
            order=1,
        )
        self.material = LessonMaterial.objects.create(
            lesson=self.lesson,
            theory='Legacy theory',
            practice='Legacy practice',
        )

    def test_known_payload_is_valid_and_unknown_type_can_be_stored_for_fallback(self):
        known = LessonBlock(
            lesson=self.lesson,
            type=LessonBlock.Type.THEORY,
            position=10,
            content={'markdown': '## Block theory\n\nText.'},
        )
        known.full_clean()

        unknown = LessonBlock(
            lesson=self.lesson,
            type='future_widget',
            position=20,
            content={'arbitrary': 'payload'},
        )
        unknown.full_clean()

    def test_known_payload_requires_expected_content(self):
        block = LessonBlock(
            lesson=self.lesson,
            type=LessonBlock.Type.THEORY,
            position=10,
            content={'wrong': 'field'},
        )

        with self.assertRaises(ValidationError):
            block.full_clean()

    def test_image_block_rejects_external_source(self):
        block = LessonBlock(
            lesson=self.lesson,
            type=LessonBlock.Type.IMAGE,
            position=10,
            content={
                'src': 'https://example.com/tracker.svg',
                'alt': 'Внешнее изображение',
            },
        )

        with self.assertRaises(ValidationError):
            block.full_clean()

    def test_blocks_are_ordered_and_rendered_with_safe_fallback(self):
        LessonBlock.objects.create(
            lesson=self.lesson,
            type=LessonBlock.Type.SUMMARY,
            position=20,
            content={'markdown': 'Краткий вывод.'},
            published=True,
        )
        LessonBlock.objects.create(
            lesson=self.lesson,
            type=LessonBlock.Type.THEORY,
            position=10,
            content={'markdown': '## Первый блок\n\nОбъяснение.'},
            published=True,
        )
        LessonBlock.objects.create(
            lesson=self.lesson,
            type='future_widget',
            position=30,
            content={'secret': 'must not be rendered'},
            published=True,
        )

        rendered = render_lesson_blocks(self.lesson.blocks.filter(published=True))

        self.assertLess(rendered.index('## Первый блок'), rendered.index('Краткий вывод.'))
        self.assertIn(':::important', rendered)
        self.assertNotIn('must not be rendered', rendered)

    def test_legacy_content_is_used_until_a_published_block_exists(self):
        self.assertEqual(
            get_lesson_stage_content(self.lesson, 'theory', self.material),
            'Legacy theory',
        )

        LessonBlock.objects.create(
            lesson=self.lesson,
            type=LessonBlock.Type.THEORY,
            position=10,
            content={'markdown': 'Block theory'},
            published=False,
        )
        self.assertEqual(
            get_lesson_stage_content(self.lesson, 'theory', self.material),
            'Legacy theory',
        )

        block = LessonBlock.objects.create(
            lesson=self.lesson,
            type=LessonBlock.Type.THEORY,
            position=20,
            content={'markdown': 'Published block'},
            published=True,
        )
        self.assertEqual(
            get_lesson_stage_content(self.lesson, 'theory', self.material),
            'Published block',
        )
        block.published = False
        block.save(update_fields=['published'])
        self.assertEqual(
            get_lesson_stage_content(self.lesson, 'theory', self.material),
            'Legacy theory',
        )
