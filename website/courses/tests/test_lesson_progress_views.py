from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from courses.models.course import Course
from courses.models.lesson_progress import LessonProgress
from courses.models.lessons import Lesson
from courses.models.module import Module
from courses.models.subject import Subject


class LessonProgressViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='progress-view-user',
            email='progress-view-user@example.com',
        )
        self.other_user = get_user_model().objects.create_user(
            username='progress-view-other',
            email='progress-view-other@example.com',
        )
        subject = Subject.objects.create(
            title='Программирование',
            description='Тестовое направление',
            slug='view-programming',
            image='subjects/images/view.png',
        )
        self.course = Course.objects.create(
            owner=self.user,
            subject=subject,
            title='Курс представлений',
            slug='view-course',
            description='Тестовый курс',
            image='courses/images/view.png',
            period=4,
            count_projects=1,
        )
        self.course.students.add(self.user)
        self.module = Module.objects.create(
            course=self.course,
            title='Модуль представлений',
            description='Тестовый модуль',
            order=1,
        )
        self.other_module = Module.objects.create(
            course=self.course,
            title='Другой модуль',
            description='Второй модуль',
            order=2,
        )
        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Первый урок представлений',
            order=1,
        )
        self.next_lesson = Lesson.objects.create(
            module=self.module,
            title='Следующий урок представлений',
            order=2,
        )
        self.other_module_lesson = Lesson.objects.create(
            module=self.other_module,
            title='Урок другого модуля',
            order=1,
        )
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.client.force_login(self.user)

    @property
    def lesson_url(self):
        return reverse(
            'courses:course_trainer_lesson',
            args=[self.course.slug, self.module.id, self.lesson.id],
        )

    @property
    def progress_url(self):
        return reverse(
            'courses:course_trainer_lesson_progress',
            args=[self.course.slug, self.module.id, self.lesson.id],
        )

    def test_first_lesson_open_creates_progress_and_exposes_steps(self):
        response = self.client.get(self.lesson_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['active_step'], 1)
        self.assertEqual(len(response.context['lesson_steps']), 5)
        self.assertTrue(
            LessonProgress.objects.filter(
                user=self.user,
                lesson=self.lesson,
            ).exists()
        )

    def test_complete_step_post_redirects_to_next_step(self):
        response = self.client.post(
            self.progress_url,
            {'action': 'complete_step', 'step': 1},
        )

        self.assertEqual(
            response.status_code,
            302,
            f'path={response.wsgi_request.path_info} '
            f'resolver={getattr(response.wsgi_request, "resolver_match", None)} '
            f'content={response.content[:80]!r}',
        )
        self.assertIn('step=2', response.url)
        progress = LessonProgress.objects.get(
            user=self.user,
            lesson=self.lesson,
        )
        self.assertEqual(progress.current_step, 2)

    def test_invalid_forward_step_returns_bad_request(self):
        response = self.client.post(
            self.progress_url,
            {'action': 'complete_step', 'step': 4},
        )

        self.assertEqual(
            response.status_code,
            400,
            f'path={response.wsgi_request.path_info} '
            f'resolver={getattr(response.wsgi_request, "resolver_match", None)}',
        )
        self.assertFalse(
            LessonProgress.objects.filter(
                user=self.user,
                lesson=self.lesson,
            ).exists()
        )

    def test_guest_is_redirected_from_progress_post(self):
        self.client.logout()

        response = self.client.post(
            self.progress_url,
            {'action': 'complete_step', 'step': 1},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/account/login/', response.url)

    def test_other_user_cannot_read_or_change_progress(self):
        self.client.force_login(self.other_user)

        response = self.client.get(self.lesson_url)
        post_response = self.client.post(
            self.progress_url,
            {'action': 'complete_step', 'step': 1},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(post_response.status_code, 404)
        self.assertFalse(LessonProgress.objects.exists())

    def test_cross_module_lesson_is_not_resolved(self):
        url = reverse(
            'courses:course_trainer_lesson',
            args=[
                self.course.slug,
                self.module.id,
                self.other_module_lesson.id,
            ],
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_context_exposes_adjacent_lessons(self):
        response = self.client.get(self.lesson_url)

        self.assertIsNone(response.context['previous_lesson'])
        self.assertEqual(response.context['next_lesson'], self.next_lesson)
