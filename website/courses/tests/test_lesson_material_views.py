from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from courses.models.course import Course
from courses.models.lesson_material import LessonMaterial
from courses.models.lessons import Lesson
from courses.models.module import Module
from courses.models.subject import Subject
from courses.templatetags.lesson_material import render_markdown


class LessonMaterialViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='student-test', email='student-test@example.com'
        )
        subject = Subject.objects.create(
            title='Программирование',
            description='Тестовое направление',
            slug='programmirovanie',
            image='subjects/images/test.png',
        )
        self.course = Course.objects.create(
            owner=self.user,
            subject=subject,
            title='ML-инженер',
            slug='ml-inzhener',
            overview='Практический курс',
            description='Техническое обучение',
            image='courses/images/test.png',
            period=8,
            count_projects=4,
        )
        self.course.students.add(self.user)
        self.module = Module.objects.create(
            course=self.course,
            title='Python для ML',
            description='Базовый модуль',
            order=1,
        )
        self.other_module = Module.objects.create(
            course=self.course,
            title='Математика',
            description='Второй модуль',
            order=2,
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Python для анализа данных',
            order=1,
        )
        self.other_lesson = Lesson.objects.create(
            module=self.other_module,
            title='Векторы и матрицы',
            order=1,
        )
        LessonMaterial.objects.create(
            lesson=self.lesson,
            objectives='Научиться работать с массивами',
            theory='Теория NumPy',
            practice='Решить практическое задание',
            self_check='Что такое broadcasting?',
            resources='[Документация](https://numpy.org/doc/stable/user/quickstart.html)',
        )
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.client.force_login(self.user)

    def test_lesson_page_renders_all_material_sections(self):
        url = f'/ru/course/{self.course.slug}/trainer/{self.module.id}/lesson/{self.lesson.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Цели обучения')
        self.assertContains(response, 'Теория')
        self.assertContains(response, 'Практика')
        self.assertContains(response, 'Самопроверка')
        self.assertContains(response, 'Источники')
        self.assertContains(response, 'Шаг 1 из 5')
        self.assertNotContains(response, 'Решить практическое задание')
        self.assertContains(response, self.lesson.title)

    def test_lesson_from_another_module_cannot_be_opened_through_selected_module(self):
        url = f'/ru/course/{self.course.slug}/trainer/{self.module.id}/lesson/{self.other_lesson.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_guest_is_redirected_to_login(self):
        self.client.logout()
        url = f'/ru/course/{self.course.slug}/trainer/{self.module.id}/lesson/{self.lesson.id}/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/account/login/', response.url)

    def test_markdown_escapes_html_and_keeps_https_links(self):
        rendered = render_markdown(
            '<script>alert(1)</script>\n\n[Документация](https://docs.python.org/)'
        )

        self.assertNotIn('<script>', rendered)
        self.assertIn('&lt;script&gt;', rendered)
        self.assertIn('href="https://docs.python.org/"', rendered)
