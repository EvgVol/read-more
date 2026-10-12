from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase

from courses.models.course import Course
from courses.models.lesson_material import LessonMaterial
from courses.models.quiz import QuizQuestion


class MlCourseEndToEndTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_ml_course', verbosity=0)
        call_command('seed_ml_materials', verbosity=0)

    def test_course_has_complete_program(self):
        course = Course.objects.get(slug='ml-inzhener')

        self.assertEqual(course.modules.count(), 7)
        self.assertEqual(sum(m.lessons.count() for m in course.modules.all()), 28)
        self.assertEqual(
            LessonMaterial.objects.filter(lesson__module__course=course).count(),
            28,
        )

    def test_enrolled_student_can_open_every_program_page(self):
        course = Course.objects.get(slug='ml-inzhener')
        owner = get_user_model().objects.get(username='ml-course-admin')
        client = Client(HTTP_HOST='127.0.0.1')
        client.force_login(owner)

        urls = [f'/ru/course/{course.slug}/trainer/']
        for module in course.modules.all():
            urls.append(f'/ru/course/{course.slug}/trainer/{module.id}/')
            for lesson in module.lessons.all():
                urls.append(
                    f'/ru/course/{course.slug}/trainer/{module.id}/lesson/{lesson.id}/'
                )

        responses = [client.get(url) for url in urls]

        self.assertEqual(len(responses), 36)
        self.assertTrue(all(response.status_code == 200 for response in responses))

    def test_docker_startup_seeds_materials_after_course(self):
        dockerfile = Path('/code/Dockerfile').read_text()
        course_seed = dockerfile.index('seed_ml_course')
        material_seed = dockerfile.index('seed_ml_materials')
        block_seed = dockerfile.index('seed_ml_lesson_blocks')
        quiz_seed = dockerfile.index('seed_ml_quiz')

        self.assertLess(course_seed, material_seed)
        self.assertLess(material_seed, block_seed)
        self.assertLess(block_seed, quiz_seed)

    def test_first_lesson_quiz_is_server_graded_and_answers_are_not_exposed(self):
        from django.core.management import call_command

        call_command('seed_ml_quiz', verbosity=0)
        course = Course.objects.get(slug='ml-inzhener')
        module = course.modules.get(title='Python для ML')
        lesson = module.lessons.get(title='Python для анализа данных')
        questions = list(QuizQuestion.objects.filter(lesson=lesson).order_by('position'))
        client = Client(HTTP_HOST='127.0.0.1')
        client.force_login(course.owner)

        page = client.get(
            f'/ru/course/{course.slug}/trainer/{module.id}/lesson/{lesson.id}/?step=2'
        )
        body = page.content.decode()
        self.assertEqual(page.status_code, 200)
        self.assertIn('Мини-тест по уроку', body)
        self.assertIn(questions[0].prompt, body)
        self.assertNotIn('correct_answers', body)

        response = client.post(
            f'/ru/course/{course.slug}/trainer/{module.id}/lesson/{lesson.id}/quiz/submit/',
            {
                f'question_{questions[0].id}': 'b',
                f'question_{questions[1].id}': ['a', 'b', 'd'],
                f'question_{questions[2].id}': 'shape',
            },
        )
        self.assertEqual(response.status_code, 302)
        result = client.get(response['Location'])
        self.assertContains(result, 'Тест пройден')
        self.assertContains(result, 'Последняя попытка:')
        self.assertContains(result, 'Освоено')
        self.assertContains(result, 'История попыток (1)')
        self.assertContains(result, 'Тесты: 1/28')
        self.assertContains(result, 'Средний результат: 100%')
        self.assertContains(result, 'Тесты: 1/4 · 100%')

        second = client.post(
            f'/ru/course/{course.slug}/trainer/{module.id}/lesson/{lesson.id}/quiz/submit/',
            {
                f'question_{questions[0].id}': 'a',
                f'question_{questions[1].id}': ['a'],
                f'question_{questions[2].id}': 'wrong',
            },
        )
        history = client.get(second['Location'])
        self.assertContains(history, 'История попыток (2)')
        self.assertContains(history, 'Повторить')
