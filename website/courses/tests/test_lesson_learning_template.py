from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from courses.models.course import Course
from courses.models.lesson_material import LessonMaterial
from courses.models.lessons import Lesson
from courses.models.module import Module
from courses.models.subject import Subject


class LessonLearningTemplateTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='learning-template-user',
            email='learning-template-user@example.com',
        )
        subject = Subject.objects.create(
            title='Программирование',
            description='Тестовое направление',
            slug='template-programming',
            image='subjects/images/template.png',
        )
        self.course = Course.objects.create(
            owner=self.user,
            subject=subject,
            title='Курс шаблонов',
            slug='template-course',
            description='Тестовый курс',
            image='courses/images/template.png',
            period=4,
            count_projects=1,
        )
        self.course.students.add(self.user)
        self.module = Module.objects.create(
            course=self.course,
            title='Модуль обучения',
            description='Тестовый модуль',
            order=1,
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Урок интерфейса',
            order=1,
        )
        LessonMaterial.objects.create(
            lesson=self.lesson,
            objectives='Цель урока',
            theory=(
                '## Как читать этот урок\n\n'
                'Подробное объяснение.\n\n'
                ':::important\nВажно читать последовательно.\n:::\n\n'
                '![Схема урока](/static/images/courses/ml-inzhener/python/01-data-flow.svg)'
            ),
            practice='Практическое задание',
            self_check='Вопрос для самопроверки',
            resources='[Источник](https://docs.python.org/3/)',
        )
        self.empty_lesson = Lesson.objects.create(
            module=self.module,
            title='Урок без материала',
            order=2,
        )
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.client.force_login(self.user)

    def url_for(self, lesson):
        return reverse(
            'courses:course_trainer_lesson',
            args=[self.course.slug, self.module.id, lesson.id],
        )

    def test_lesson_has_five_step_learning_layout(self):
        response = self.client.get(self.url_for(self.lesson))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Шаг 1 из 5')
        self.assertContains(response, 'Цели обучения')
        self.assertContains(response, 'Теория')
        self.assertContains(response, 'Практика')
        self.assertContains(response, 'Самопроверка')
        self.assertContains(response, 'Источники')
        self.assertContains(response, 'Отметить этап')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(response, 'Урок начат')
        self.assertContains(response, 'course-learning')

    def test_requested_step_displays_only_that_section(self):
        response = self.client.get(f'{self.url_for(self.lesson)}?step=2')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Шаг 2 из 5')
        self.assertContains(response, 'Подробное объяснение.')
        self.assertContains(response, 'Оглавление урока')
        self.assertContains(response, 'href="#kak-chitat-etot-urok"')
        self.assertContains(response, 'lesson-callout')
        self.assertContains(response, '<figure', html=False)
        self.assertContains(response, 'aria-label="Навигация по разделам урока"')
        self.assertNotContains(response, 'Цель урока')

    def test_missing_material_shows_empty_state_without_completion_form(self):
        response = self.client.get(self.url_for(self.empty_lesson))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Материал для этого урока ещё готовится.')
        self.assertNotContains(response, 'Отметить этап')
