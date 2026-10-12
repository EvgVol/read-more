from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase

from courses.models.course import Course
from courses.models.lesson_material import LessonMaterial


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

        self.assertLess(course_seed, material_seed)
