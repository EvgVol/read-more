from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse

from courses.models.course import Course
from courses.models.audit import CourseAuditRun


class CourseAuditViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_ml_course', verbosity=0)
        call_command('seed_ml_materials', verbosity=0)
        call_command('seed_ml_quiz', verbosity=0)
        cls.course = Course.objects.get(slug='ml-inzhener')

    def test_anonymous_user_is_redirected_to_login(self):
        response = Client().get(
            reverse('courses:course_audit', kwargs={'slug': self.course.slug})
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/account/login/', response['Location'])

    def test_student_cannot_open_editor_audit(self):
        student = get_user_model().objects.create_user(username='course-student')
        self.course.students.add(student)
        client = Client()
        client.force_login(student)

        response = client.get(
            reverse('courses:course_audit', kwargs={'slug': self.course.slug})
        )

        self.assertEqual(response.status_code, 404)

    def test_course_owner_sees_editor_audit(self):
        client = Client()
        client.force_login(self.course.owner)

        response = client.get(
            reverse('courses:course_audit', kwargs={'slug': self.course.slug})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Отчёт качества курса')
        self.assertContains(response, '>28<')
        self.assertContains(response, '>84<')
        self.assertContains(response, 'уроков')
        self.assertContains(response, 'quiz-вопроса')
        self.assertContains(response, 'Python для анализа данных')
        self.assertContains(response, 'Аудит пройден')

    def test_audit_rows_link_to_lessons_and_support_issue_filter(self):
        client = Client()
        client.force_login(self.course.owner)

        response = client.get(
            reverse('courses:course_audit', kwargs={'slug': self.course.slug})
        )

        self.assertContains(
            response,
            reverse(
                'courses:course_trainer_lesson',
                kwargs={
                    'slug': self.course.slug,
                    'module_id': self.course.modules.first().id,
                    'lesson_id': self.course.modules.first().lessons.first().id,
                },
            ),
        )
        self.assertContains(response, 'Только с замечаниями')

        filtered = client.get(
            reverse('courses:course_audit', kwargs={'slug': self.course.slug}),
            {'filter': 'issues'},
        )

        self.assertEqual(filtered.status_code, 200)
        self.assertContains(filtered, 'Все уроки прошли аудит')

    def test_owner_can_download_current_audit_as_csv(self):
        client = Client()
        client.force_login(self.course.owner)

        response = client.get(
            reverse('courses:course_audit', kwargs={'slug': self.course.slug}),
            {'format': 'csv', 'filter': 'issues'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertIn('Модуль,Урок', response.content.decode('utf-8-sig'))

    def test_audit_summary_exposes_issue_categories(self):
        client = Client()
        client.force_login(self.course.owner)

        response = client.get(
            reverse('courses:course_audit', kwargs={'slug': self.course.slug})
        )

        self.assertContains(response, 'Типы замечаний')
        self.assertContains(response, 'Quiz')

    def test_broken_practice_is_visible_with_category_and_csv_detail(self):
        material = self.course.modules.first().lessons.first().material
        material.practice = 'Слишком короткая практика.'
        material.save(update_fields=['practice', 'updated'])
        client = Client()
        client.force_login(self.course.owner)
        url = reverse('courses:course_audit', kwargs={'slug': self.course.slug})

        page = client.get(url)
        self.assertContains(page, 'Нужны исправления')
        self.assertContains(page, 'Практика')
        self.assertContains(page, 'Есть замечания')
        self.assertContains(page, material.lesson.title)

        csv_response = client.get(url, {'format': 'csv', 'filter': 'issues'})
        csv_body = csv_response.content.decode('utf-8-sig')
        self.assertIn('Практика', csv_body)
        self.assertIn(material.lesson.title, csv_body)

    def test_owner_can_save_audit_run_and_open_history(self):
        client = Client()
        client.force_login(self.course.owner)
        run_url = reverse(
            'courses:course_audit_run',
            kwargs={'slug': self.course.slug},
        )

        response = client.post(run_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(CourseAuditRun.objects.count(), 1)
        run = CourseAuditRun.objects.get()
        self.assertTrue(run.passed)
        self.assertEqual(run.lessons_count, 28)
        self.assertEqual(run.published_questions_count, 84)

        history = client.get(
            reverse(
                'courses:course_audit_history',
                kwargs={'slug': self.course.slug},
            )
        )
        self.assertEqual(history.status_code, 200)
        self.assertContains(history, 'История аудитов')
        self.assertContains(history, 'Аудит пройден')

    def test_student_cannot_start_audit_run(self):
        student = get_user_model().objects.create_user(username='audit-student')
        self.course.students.add(student)
        client = Client()
        client.force_login(student)

        response = client.post(
            reverse(
                'courses:course_audit_run',
                kwargs={'slug': self.course.slug},
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(CourseAuditRun.objects.count(), 0)

    def test_owner_can_compare_two_saved_audits(self):
        client = Client()
        client.force_login(self.course.owner)
        run_url = reverse(
            'courses:course_audit_run',
            kwargs={'slug': self.course.slug},
        )
        client.post(run_url)
        first_run = CourseAuditRun.objects.get()

        material = self.course.modules.first().lessons.first().material
        material.practice = 'Слишком короткая практика.'
        material.save(update_fields=['practice', 'updated'])
        client.post(run_url)
        second_run = CourseAuditRun.objects.order_by('-created', '-id').first()

        response = client.get(
            reverse(
                'courses:course_audit_compare',
                kwargs={'slug': self.course.slug},
            ),
            {'left': first_run.id, 'right': second_run.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Сравнение аудитов')
        self.assertContains(response, 'Изменения')
        self.assertContains(response, material.lesson.title)
        self.assertContains(response, 'Практика')
