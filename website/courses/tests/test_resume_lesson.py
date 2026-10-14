from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from courses.models.course import Course
from courses.models.lesson_progress import LessonProgress
from courses.models.lessons import Lesson
from courses.models.module import Module
from courses.models.subject import Subject
from courses.services.lesson_progress import resume_lesson


def make_course(owner, slug='resume-course'):
    subject = Subject.objects.create(
        title='Предмет', description='d', slug=slug + '-subject',
        image='subjects/images/resume.png',
    )
    course = Course.objects.create(
        owner=owner, subject=subject, title='Resume course', slug=slug,
        description='test', image='courses/images/resume.png',
        period=4, count_projects=1,
    )
    return course


def make_modules_lessons(course, modules_count=2, lessons_per_module=2):
    """Create an ordered grid of modules/lessons, return (modules, lessons)."""
    modules, lessons = [], []
    for m in range(1, modules_count + 1):
        module = Module.objects.create(
            course=course, title=f'M{m}', description='m', order=m)
        modules.append(module)
        for l in range(1, lessons_per_module + 1):
            lesson = Lesson.objects.create(
                module=module, title=f'L{m}-{l}', order=l)
            lessons.append(lesson)
    return modules, lessons


class ResumeLessonServiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='resume-user', email='resume@example.com',
            password='pass123')
        self.course = make_course(self.user)
        self.modules, self.lessons = make_modules_lessons(
            self.course, modules_count=2, lessons_per_module=2)
        # lessons: L1-1, L1-2, L2-1, L2-2

    def _progress(self, lesson, status, step=1, opened_offset=0):
        return LessonProgress.objects.create(
            user=self.user, lesson=lesson, status=status,
            current_step=step,
            last_opened_at=timezone.now() + timedelta(minutes=opened_offset),
            started_at=timezone.now(),
        )

    def test_no_progress_returns_first_lesson_step_1(self):
        lesson, step = resume_lesson(user=self.user, course=self.course)
        self.assertEqual(lesson, self.lessons[0])
        self.assertEqual(step, 1)

    def test_in_progress_lesson_wins_at_its_current_step(self):
        self._progress(self.lessons[2], LessonProgress.Status.IN_PROGRESS,
                       step=3)
        self._progress(self.lessons[0], LessonProgress.Status.COMPLETED)
        lesson, step = resume_lesson(user=self.user, course=self.course)
        self.assertEqual(lesson, self.lessons[2])
        self.assertEqual(step, 3)

    def test_most_recent_in_progress_wins(self):
        self._progress(self.lessons[0], LessonProgress.Status.IN_PROGRESS,
                       step=2, opened_offset=-30)
        self._progress(self.lessons[3], LessonProgress.Status.IN_PROGRESS,
                       step=4, opened_offset=0)
        lesson, step = resume_lesson(user=self.user, course=self.course)
        self.assertEqual(lesson, self.lessons[3])
        self.assertEqual(step, 4)

    def test_completed_then_first_unstarted(self):
        self._progress(self.lessons[0], LessonProgress.Status.COMPLETED)
        self._progress(self.lessons[1], LessonProgress.Status.COMPLETED)
        lesson, step = resume_lesson(user=self.user, course=self.course)
        self.assertEqual(lesson, self.lessons[2])
        self.assertEqual(step, 1)

    def test_all_completed_returns_most_recent(self):
        self._progress(self.lessons[0], LessonProgress.Status.COMPLETED,
                       opened_offset=-30)
        self._progress(self.lessons[1], LessonProgress.Status.COMPLETED,
                       opened_offset=-20)
        self._progress(self.lessons[2], LessonProgress.Status.COMPLETED,
                       opened_offset=-10)
        self._progress(self.lessons[3], LessonProgress.Status.COMPLETED,
                       opened_offset=0)
        lesson, step = resume_lesson(user=self.user, course=self.course)
        self.assertEqual(lesson, self.lessons[3])

    def test_no_lessons_returns_none(self):
        for module in self.modules:
            module.lessons.all().delete()
        self.assertIsNone(
            resume_lesson(user=self.user, course=self.course))


class ResumeLessonViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='resume-view', email='resume-view@example.com',
            password='pass123')
        self.course = make_course(self.user, slug='resume-view-course')
        self.modules, self.lessons = make_modules_lessons(
            self.course, modules_count=1, lessons_per_module=3)
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.client.force_login(self.user)

    def _entry_url(self):
        return reverse('courses:course_trainer', args=[self.course.slug])

    def test_entry_redirects_to_in_progress_lesson_and_step(self):
        LessonProgress.objects.create(
            user=self.user, lesson=self.lessons[1],
            status=LessonProgress.Status.IN_PROGRESS, current_step=3,
            last_opened_at=timezone.now(), started_at=timezone.now(),
        )
        response = self.client.get(self._entry_url())
        self.assertEqual(response.status_code, 302)
        expected = reverse(
            'courses:course_trainer_lesson',
            args=[self.course.slug, self.modules[0].id, self.lessons[1].id],
        )
        self.assertEqual(response.url, expected + '?step=3')

    def test_entry_redirects_to_first_lesson_when_fresh(self):
        response = self.client.get(self._entry_url())
        self.assertEqual(response.status_code, 302)
        self.assertIn(f'{self.lessons[0].id}', response.url)
        self.assertIn('step=1', response.url)

    def test_entry_without_lessons_renders_empty_module_page(self):
        self.modules[0].lessons.all().delete()
        response = self.client.get(self._entry_url())
        self.assertEqual(response.status_code, 200)

    def test_module_page_is_not_redirected(self):
        url = reverse('courses:course_trainer_module',
                      args=[self.course.slug, self.modules[0].id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class EnrollButtonOpensCurrentTabTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tab-user', email='tab@example.com',
            password='pass123')
        self.course = make_course(self.user, slug='tab-course')
        self.client = Client(HTTP_HOST='127.0.0.1')
        self.client.force_login(self.user)

    def test_enroll_forms_do_not_open_new_tabs(self):
        import re
        response = self.client.get(reverse(
            'courses:course_detail', args=[self.course.pk]))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        enroll_url = reverse('courses:student_enroll_course')
        enroll_forms = [
            tag for tag in re.findall(r'<form[^>]*', content)
            if enroll_url in tag
        ]
        self.assertTrue(enroll_forms, 'enroll form not found on course detail')
        # Neither the hero nor the bottom CTA enroll form may open a tab.
        for tag in enroll_forms:
            self.assertNotIn('target="_blank"', tag)