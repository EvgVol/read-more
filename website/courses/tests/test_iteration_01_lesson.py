import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import Client
from django.test import TestCase

from courses.models.course import Course
from courses.models.lesson_block import LessonBlock
from courses.models.lesson_material import LessonMaterial
from courses.models.lesson_progress import LessonProgress
from courses.models.quiz import QuizQuestion
from courses.lesson_examples.python_data_summary import summarize_orders


class Iteration01PythonLessonTests(TestCase):
    def setUp(self):
        call_command('seed_ml_course', verbosity=0)
        call_command('seed_ml_materials', verbosity=0)
        call_command('seed_ml_lesson_blocks', verbosity=0)
        call_command('seed_ml_quiz', verbosity=0)

    def lesson(self):
        return Course.objects.get(slug='ml-inzhener').modules.get(
            title='Python для ML'
        ).lessons.get(title='Python для анализа данных')

    def test_checkpoint_b_seed_publishes_only_the_reference_lesson(self):
        call_command('seed_ml_lesson_2717', verbosity=0)
        lesson = self.lesson()

        self.assertEqual(lesson.title, 'Python для анализа данных')
        self.assertEqual(
            list(lesson.blocks.order_by('position').values_list('type', flat=True)),
            ['theory'] * 9 + ['image'] * 5 + ['summary'],
        )
        self.assertEqual(lesson.blocks.filter(published=True).count(), 15)
        self.assertEqual(
            LessonBlock.objects.filter(lesson__module__course_id=1)
            .exclude(lesson=lesson).count(),
            0,
        )

    def test_checkpoint_b_quiz_has_twelve_educationally_tagged_questions(self):
        call_command('seed_ml_lesson_2717', verbosity=0)
        questions = QuizQuestion.objects.filter(lesson=self.lesson()).order_by('position')

        self.assertEqual(questions.count(), 12)
        for question in questions:
            self.assertTrue(question.metadata['objective'])
            self.assertIn(question.metadata['difficulty'], {'basic', 'intermediate', 'advanced'})
            self.assertTrue(question.metadata['topic'])
            self.assertTrue(question.explanation)

    def test_checkpoint_b_preserves_progress_and_uses_decimal_amounts(self):
        lesson = self.lesson()
        progress = LessonProgress.objects.create(
            user=Course.objects.get(slug='ml-inzhener').owner,
            lesson=lesson,
            status=LessonProgress.Status.IN_PROGRESS,
            current_step=3,
        )
        call_command('seed_ml_lesson_2717', verbosity=0)

        progress.refresh_from_db()
        self.assertEqual(progress.current_step, 3)
        result = summarize_orders([
            {'order_id': 'A-1', 'amount': '0.10', 'status': 'paid'},
            {'order_id': 'A-2', 'amount': '0.20', 'status': 'pending'},
        ])
        self.assertEqual(result['amount_total'], '0.30')
        self.assertEqual(result['errors'], [])

    def test_checkpoint_b_lesson_page_renders_all_sections_visuals_and_quiz(self):
        call_command('seed_ml_lesson_2717', verbosity=0)
        course = Course.objects.get(slug='ml-inzhener')
        client = Client()
        client.force_login(course.owner)
        url = f'/ru/course/{course.slug}/trainer/{lesson_module_id(course)}/lesson/{self.lesson().id}/?step=2'

        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Зачем Python используется в анализе данных')
        self.assertContains(response, 'Структура Python-проекта')
        self.assertContains(response, 'block-10-1-zachem-python-ispolzuetsya-v-analize-dannyh')
        self.assertContains(response, '01-project-structure.svg')
        self.assertContains(response, 'Цикл тестирования')
        self.assertContains(response, 'question_')
        self.assertNotContains(response, 'javascript:')

    def test_snapshot_restore_returns_content_without_touching_progress(self):
        lesson = self.lesson()
        progress = LessonProgress.objects.create(
            user=Course.objects.get(slug='ml-inzhener').owner,
            lesson=lesson,
            status=LessonProgress.Status.IN_PROGRESS,
            current_step=4,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'lesson.json'
            call_command('snapshot_ml_lesson', str(path), verbosity=0)
            call_command('seed_ml_lesson_2717', verbosity=0)
            call_command('restore_ml_lesson', str(path), verbosity=0)

        self.assertEqual(lesson.blocks.count(), 5)
        self.assertEqual(lesson.quiz_questions.count(), 3)
        progress.refresh_from_db()
        self.assertEqual(progress.current_step, 4)


def lesson_module_id(course):
    return course.modules.get(title='Python для ML').id
import tempfile
from pathlib import Path
