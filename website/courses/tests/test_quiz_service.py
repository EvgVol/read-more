from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from courses.models.course import Course
from courses.models.lessons import Lesson
from courses.models.module import Module
from courses.models.quiz import QuizAnswer, QuizAttempt, QuizQuestion
from courses.models.subject import Subject
from courses.services.quiz import course_quiz_progress, normalize_short_answer, submit_quiz


class QuizServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='quiz-user', email='quiz-user@example.com'
        )
        subject = Subject.objects.create(
            title='Программирование', description='Тест', slug='quiz-subject', image='subjects/quiz.png'
        )
        course = Course.objects.create(
            owner=self.user, subject=subject, title='Quiz course', slug='quiz-course',
            description='Тест', image='courses/quiz.png', period=1, count_projects=1,
        )
        module = Module.objects.create(course=course, title='Модуль', description='Тест', order=1)
        self.lesson = Lesson.objects.create(module=module, title='Урок', order=1)
        self.single = QuizQuestion.objects.create(
            lesson=self.lesson, type=QuizQuestion.Type.SINGLE, position=10,
            prompt='Выберите B', options=[{'id': 'a', 'text': 'A'}, {'id': 'b', 'text': 'B'}],
            correct_answers=['b'], published=True,
        )
        self.multiple = QuizQuestion.objects.create(
            lesson=self.lesson, type=QuizQuestion.Type.MULTIPLE, position=20,
            prompt='Выберите A и B', options=[{'id': 'a', 'text': 'A'}, {'id': 'b', 'text': 'B'}, {'id': 'c', 'text': 'C'}],
            correct_answers=['a', 'b'], published=True,
        )
        self.short = QuizQuestion.objects.create(
            lesson=self.lesson, type=QuizQuestion.Type.SHORT, position=30,
            prompt='Введите shape', correct_answers=['shape'], published=True,
        )

    def test_short_answer_normalization_is_explicit(self):
        self.assertEqual(normalize_short_answer('  SHAPE\n '), 'shape')

    def test_submit_grades_exact_and_partial_answers_and_stores_attempt(self):
        attempt = submit_quiz(
            user=self.user,
            lesson=self.lesson,
            answers={str(self.single.id): 'b', str(self.multiple.id): ['a'], str(self.short.id): ' SHAPE '},
        )

        self.assertEqual(attempt.total_points, 3)
        self.assertEqual(str(attempt.earned_points), '2.50')
        self.assertTrue(attempt.passed)
        self.assertEqual(attempt.answers.count(), 3)
        self.assertTrue(
            QuizAnswer.objects.get(attempt=attempt, question=self.short).is_correct
        )

    def test_unpublished_questions_are_not_graded(self):
        self.multiple.published = False
        self.multiple.save(update_fields=['published'])

        attempt = submit_quiz(
            user=self.user,
            lesson=self.lesson,
            answers={str(self.single.id): 'b', str(self.multiple.id): ['a'], str(self.short.id): 'shape'},
        )

        self.assertEqual(attempt.answers.count(), 2)
        self.assertEqual(attempt.total_points, 2)

    def test_empty_quiz_is_rejected(self):
        QuizQuestion.objects.filter(lesson=self.lesson).update(published=False)

        with self.assertRaises(ValidationError):
            submit_quiz(user=self.user, lesson=self.lesson, answers={})

    def test_course_progress_uses_latest_attempt_only(self):
        first = submit_quiz(
            user=self.user,
            lesson=self.lesson,
            answers={str(self.single.id): 'b', str(self.multiple.id): ['a', 'b'], str(self.short.id): 'shape'},
        )
        self.assertTrue(first.passed)
        submit_quiz(
            user=self.user,
            lesson=self.lesson,
            answers={str(self.single.id): 'a', str(self.multiple.id): [], str(self.short.id): 'wrong'},
        )

        progress = course_quiz_progress(user=self.user, course=self.lesson.module.course)

        self.assertEqual(progress['total_quizzes'], 1)
        self.assertEqual(progress['attempted_quizzes'], 1)
        self.assertEqual(progress['passed_quizzes'], 0)
        self.assertEqual(progress['average_percent'], 0)
