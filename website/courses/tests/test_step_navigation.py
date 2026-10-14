from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from courses.models.course import Course
from courses.models.lesson_material import LessonMaterial
from courses.models.lessons import Lesson
from courses.models.module import Module
from courses.models.subject import Subject


def _make_course(user):
    subject = Subject.objects.create(
        title='Направление',
        description='Дирекция',
        slug='step-navigation-direction',
        image='subjects/images/step.png',
    )
    course = Course.objects.create(
        owner=user,
        subject=subject,
        title='Курс навигации',
        slug='step-navigation-course',
        description='Курс',
        image='courses/images/step.png',
        period=4,
        count_projects=1,
    )
    course.students.add(user)
    module = Module.objects.create(
        course=course,
        title='Модуль навигации',
        description='Модуль',
        order=1,
    )
    lesson = Lesson.objects.create(
        module=module,
        title='Урок навигации',
        order=1,
    )
    LessonMaterial.objects.create(
        lesson=lesson,
        objectives='Уникальные цели урока',
        theory='## Теория навигации\n\nСодержание теории.',
        practice='Уникальная практика урока',
        self_check='Уникальная самопроверка урока',
        resources='Уникальные источники урока',
    )
    return course, module, lesson


class LessonStepFragmentTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='step-fragment-user',
            email='step-fragment-user@example.com',
        )
        self.other_user = get_user_model().objects.create_user(
            username='step-fragment-other',
            email='step-fragment-other@example.com',
        )
        self.course, self.module, self.lesson = _make_course(self.user)
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.client.force_login(self.user)

    @property
    def fragment_url(self):
        return reverse(
            'courses:course_trainer_lesson_step',
            args=[self.course.slug, self.module.id, self.lesson.id],
        )

    def test_fragment_returns_only_the_requested_step(self):
        response = self.client.get(f'{self.fragment_url}?step=3')

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn('course-learning__stage-region', body)
        self.assertIn('course-learning__stepper', body)
        self.assertIn('Шаг 3 из 5', body)
        self.assertIn('Уникальная практика урока', body)
        # Content of other steps must not leak into the fragment.
        self.assertNotIn('Уникальные цели урока', body)
        self.assertNotIn('Уникальная самопроверка урока', body)
        self.assertNotIn('Уникальные источники урока', body)
        # The fragment is a partial page, not a full HTML document.
        self.assertNotIn('<html', body)

    def test_fragment_defaults_to_saved_step_without_query(self):
        from courses.services.lesson_progress import complete_step

        complete_step(user=self.user, lesson=self.lesson, step=1)

        response = self.client.get(self.fragment_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Шаг 2 из 5', response.content.decode())

    def test_fragment_clamps_out_of_range_steps(self):
        # step=0 clamps up to 1, step=99 clamps down to 5, non-numeric
        # falls back to the saved (current) step.
        low = self.client.get(f'{self.fragment_url}?step=0')
        self.assertEqual(low.status_code, 200)
        self.assertIn('Шаг 1 из 5', low.content.decode())

        high = self.client.get(f'{self.fragment_url}?step=99')
        self.assertEqual(high.status_code, 200)
        self.assertIn('Шаг 5 из 5', high.content.decode())

        junk = self.client.get(f'{self.fragment_url}?step=abc')
        self.assertEqual(junk.status_code, 200)
        self.assertIn('Шаг 1 из 5', junk.content.decode())

    def test_guest_fragment_is_redirected_to_login(self):
        self.client.logout()

        response = self.client.get(self.fragment_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/account/login/', response.url)

    def test_other_user_cannot_read_fragment(self):
        self.client.force_login(self.other_user)

        response = self.client.get(self.fragment_url)

        self.assertEqual(response.status_code, 404)

    def test_trainer_page_wires_up_instant_step_navigation(self):
        lesson_url = reverse(
            'courses:course_trainer_lesson',
            args=[self.course.slug, self.module.id, self.lesson.id],
        )
        response = self.client.get(lesson_url)

        body = response.content.decode()
        self.assertEqual(response.status_code, 200)
        # The page exposes the fragment endpoint for the current lesson and
        # loads the step-switching script; every step link is a plain anchor
        # so navigation works without JavaScript too.
        self.assertIn(self.fragment_url, body)
        self.assertIn("static/js/course-lesson-steps.js", body)
        self.assertIn('course-learning__stage-region', body)
        self.assertIn('data-step="2"', body)
        self.assertIn('href="?step=2"', body)