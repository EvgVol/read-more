from django.core.management import call_command
from django.test import TestCase

from courses.models.course import Course
from courses.models.lesson_block import LessonBlock
from courses.models.lesson_progress import LessonProgress
from courses.models.quiz import QuizQuestion


class Iteration02NumpyLessonTests(TestCase):
    def setUp(self):
        call_command('seed_ml_course', verbosity=0)
        call_command('seed_ml_materials', verbosity=0)
        call_command('seed_ml_lesson_blocks', verbosity=0)
        call_command('seed_ml_python_lesson_blocks', verbosity=0)
        call_command('seed_ml_quiz', verbosity=0)

    def lesson(self):
        return Course.objects.get(slug='ml-inzhener').modules.get(
            title='Python для ML'
        ).lessons.get(title='NumPy и векторные вычисления')

    def test_seed_publishes_only_numpy_lesson_blocks(self):
        other_blocks_before = LessonBlock.objects.exclude(lesson=self.lesson()).count()
        call_command('seed_ml_lesson_2718', verbosity=0)
        lesson = self.lesson()

        self.assertGreaterEqual(lesson.blocks.filter(published=True).count(), 8)
        self.assertEqual(lesson.blocks.filter(type=LessonBlock.Type.IMAGE).count(), 3)
        self.assertEqual(
            LessonBlock.objects.exclude(lesson=lesson).count(),
            other_blocks_before,
        )

    def test_numpy_quiz_has_metadata_and_preserves_progress(self):
        lesson = self.lesson()
        progress = LessonProgress.objects.create(
            user=Course.objects.get(slug='ml-inzhener').owner,
            lesson=lesson,
            status=LessonProgress.Status.IN_PROGRESS,
            current_step=2,
        )
        call_command('seed_ml_lesson_2718', verbosity=0)

        questions = QuizQuestion.objects.filter(lesson=lesson, published=True)
        self.assertEqual(questions.count(), 9)
        for question in questions:
            self.assertTrue(question.metadata['objective'])
            self.assertIn(question.metadata['topic'], {'shape', 'broadcasting', 'dtype', 'randomness'})
        progress.refresh_from_db()
        self.assertEqual(progress.current_step, 2)
