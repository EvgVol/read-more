from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from sorl.thumbnail import get_thumbnail

from courses.models.course import Course

STATIC_ROOT = Path(__file__).resolve().parents[2] / 'static'

COURSE_IMAGE_PATHS = (
    'images/courses/ml-inzhener/hero.png',
    'images/courses/ml-inzhener/advantages/1.png',
    'images/courses/ml-inzhener/advantages/2.png',
    'images/courses/ml-inzhener/advantages/3.png',
    'images/courses/ml-inzhener/advantages/4.png',
    'images/subjects/programming.png',
)
TECHNOLOGY_LOGO_PATHS = (
    'images/courses/ml-inzhener/logos/python.svg',
    'images/courses/ml-inzhener/logos/numpy.svg',
    'images/courses/ml-inzhener/logos/pandas.svg',
    'images/courses/ml-inzhener/logos/scikit-learn.svg',
    'images/courses/ml-inzhener/logos/pytorch.svg',
    'images/courses/ml-inzhener/logos/sql.svg',
    'images/courses/ml-inzhener/logos/docker.svg',
)
LESSON_IMAGE_PATHS = (
    'images/courses/ml-inzhener/python/02-boundaries.svg',
    'images/courses/ml-inzhener/python/03-validation-loop.svg',
    'images/courses/ml-inzhener/python/01-project-structure.svg',
    'images/courses/ml-inzhener/visualization/01-chart-anatomy.svg',
    'images/courses/ml-inzhener/visualization/02-chart-choice.svg',
)


class CourseLandingAssetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_ml_course', verbosity=0)
        call_command('seed_ml_materials', verbosity=0)
        call_command('seed_ml_lesson_images', verbosity=0)
        cls.owner = get_user_model().objects.get(username='ml-course-admin')

    def test_landing_assets_exist_in_static(self):
        for path in COURSE_IMAGE_PATHS + TECHNOLOGY_LOGO_PATHS + LESSON_IMAGE_PATHS:
            self.assertTrue((STATIC_ROOT / path).exists(), f'missing asset: {path}')

    def test_course_images_are_not_the_old_gray_placeholder(self):
        course = Course.objects.get(slug='ml-inzhener')
        self.assertTrue(course.image.name.endswith('ml-engineer.png'))
        for index, advantage in enumerate(course.advantages.all(), start=1):
            self.assertEqual(advantage.image.name, f'courses/advantages/images/ml-advantage-{index}.png')
        self.assertEqual(course.subject.image.name, 'subjects/images/programming.png')

    def test_landing_page_renders_hero_advantages_and_logos(self):
        course = Course.objects.get(slug='ml-inzhener')
        client = Client(HTTP_HOST='127.0.0.1')
        client.force_login(self.owner)

        response = client.get(f'/ru/course/{course.pk}/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()

        # Hero and advantages are rendered through sorl.thumbnail, so assert
        # the exact thumbnail URLs the template produces.
        hero_url = get_thumbnail(course.image, '600x370', crop='center').url
        self.assertIn(hero_url, content)
        for advantage in course.advantages.all():
            url = get_thumbnail(
                advantage.image, '100x100', crop='center', upscale=True
            ).url
            self.assertIn(url, content)
        # Technology logos: local static SVGs instead of external website URLs.
        for path in TECHNOLOGY_LOGO_PATHS:
            self.assertIn(f'/static/{path}', content)
        self.assertNotIn('src="https://www.python.org/"', content)

    def test_python_module_lessons_render_their_illustrations(self):
        course = Course.objects.get(slug='ml-inzhener')
        client = Client(HTTP_HOST='127.0.0.1')
        client.force_login(self.owner)

        expected = {
            'Pandas и подготовка таблиц': (
                '/static/images/courses/ml-inzhener/python/02-boundaries.svg',
                '/static/images/courses/ml-inzhener/python/03-validation-loop.svg',
            ),
            'Git, окружения и Jupyter': (
                '/static/images/courses/ml-inzhener/python/01-project-structure.svg',
            ),
            'Визуализация данных': (
                '/static/images/courses/ml-inzhener/visualization/01-chart-anatomy.svg',
                '/static/images/courses/ml-inzhener/visualization/02-chart-choice.svg',
            ),
        }
        for module in course.modules.all():
            for lesson in module.lessons.all():
                if lesson.title not in expected:
                    continue
                response = client.get(
                    f'/ru/course/{course.slug}/trainer/{module.id}/lesson/{lesson.id}/?step=2'
                )
                self.assertEqual(response.status_code, 200, lesson.title)
                content = response.content.decode()
                for src in expected[lesson.title]:
                    self.assertIn(src, content, f'{lesson.title} missing {src}')