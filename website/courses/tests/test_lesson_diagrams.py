from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase

from courses.management.commands.ml_theory import LESSON_DIAGRAMS, build_theory
from courses.models.course import Course
from courses.models.lessons import Lesson

STATIC_ROOT = Path(__file__).resolve().parents[2] / 'static'


class LessonDiagramTests(TestCase):
    """Every diagram-based lesson shows its SVG on the theory step."""

    @classmethod
    def setUpTestData(cls):
        call_command('seed_ml_course', verbosity=0)
        call_command('seed_ml_materials', verbosity=0)
        cls.owner = get_user_model().objects.get(username='ml-course-admin')

    def test_all_diagram_assets_exist_in_static(self):
        self.assertEqual(len(LESSON_DIAGRAMS), 23)
        for title, (src, alt) in LESSON_DIAGRAMS.items():
            self.assertTrue(alt, f'{title}: empty alt')
            rel = src.removeprefix('/static/')
            self.assertTrue(
                (STATIC_ROOT / rel).is_file(),
                f'{title}: missing asset {src}',
            )

    def test_build_theory_injects_diagram_after_h1(self):
        for title, (src, alt) in LESSON_DIAGRAMS.items():
            theory = build_theory(title)
            self.assertIn(f'![{alt}]({src})', theory, title)
            # the diagram sits right after the H1, before the first section
            h1 = theory.index('# ')
            img = theory.index('![')
            first_section = theory.index('## ')
            self.assertLess(h1, img)
            self.assertLess(img, first_section, title)

    def test_block_based_lessons_keep_their_own_illustrations(self):
        # These lessons attach images via published LessonBlocks, so the
        # theory generator must not also inject one.
        for title in (
            'Python для анализа данных',
            'NumPy и векторные вычисления',
            'Pandas и подготовка таблиц',
            'Git, окружения и Jupyter',
            'Визуализация данных',
        ):
            self.assertNotIn(title, LESSON_DIAGRAMS, title)
            theory = build_theory(title)
            # These lessons attach illustrations via published LessonBlocks, so
            # the generator must not also inject one of the diagram SVGs.
            for src in {src for src, _ in LESSON_DIAGRAMS.values()}:
                self.assertNotIn(src, theory, f'{title}: leaked {src}')

    def test_diagrams_render_on_theory_step(self):
        course = Course.objects.get(slug='ml-inzhener')
        client = Client(HTTP_HOST='127.0.0.1')
        client.force_login(self.owner)

        lessons = {lesson.title: lesson for lesson in Lesson.objects.filter(module__course=course)}
        rendered = 0
        for title, (src, alt) in LESSON_DIAGRAMS.items():
            lesson = lessons.get(title)
            self.assertIsNotNone(lesson, f'lesson not seeded: {title}')
            response = client.get(
                f'/ru/course/{course.slug}/trainer/{lesson.module_id}/lesson/{lesson.id}/?step=2'
            )
            self.assertEqual(response.status_code, 200, title)
            content = response.content.decode()
            self.assertIn(src, content, f'{title} missing {src}')
            rendered += 1
        self.assertEqual(rendered, 23)