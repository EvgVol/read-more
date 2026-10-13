from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models.course import Course
from courses.models.lesson_block import LessonBlock


# (module, lesson, position, src, alt, label)
IMAGE_BLOCKS = (
    (
        'Python для ML',
        'Pandas и подготовка таблиц',
        15,
        '/static/images/courses/ml-inzhener/python/02-boundaries.svg',
        'Сырые данные проходят через проверяемые правила preprocessing и '
        'превращаются в признаки, доступные модели',
        'Границы preprocessing',
    ),
    (
        'Python для ML',
        'Pandas и подготовка таблиц',
        25,
        '/static/images/courses/ml-inzhener/python/03-validation-loop.svg',
        'Цикл проверки результата преобразования данных',
        'Цикл проверки',
    ),
    (
        'Python для ML',
        'Git, окружения и Jupyter',
        15,
        '/static/images/courses/ml-inzhener/python/01-project-structure.svg',
        'Дерево проекта с каталогами data, src, tests и файлами README и '
        'pyproject',
        'Структура проекта',
    ),
    (
        'Анализ данных',
        'Визуализация данных',
        15,
        '/static/images/courses/ml-inzhener/visualization/01-chart-anatomy.svg',
        'Вопрос, оси, данные и вывод связаны в последовательный путь '
        'чтения графика',
        'Анатомия графика',
    ),
    (
        'Анализ данных',
        'Визуализация данных',
        25,
        '/static/images/courses/ml-inzhener/visualization/02-chart-choice.svg',
        'Исследовательский вопрос определяет подходящий тип графика',
        'Выбор типа графика',
    ),
)


class Command(BaseCommand):
    help = (
        'Attach published illustration blocks to the lessons that already '
        'have a seeded theory blueprint.'
    )

    @transaction.atomic
    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        if course is None:
            raise CommandError('Course "ml-inzhener" does not exist. Run seed_ml_course first.')

        modules = {module.title: module for module in course.modules.all()}
        published = 0
        for module_title, lesson_title, position, src, alt, label in IMAGE_BLOCKS:
            module = modules.get(module_title)
            if module is None:
                raise CommandError(f'Module "{module_title}" was not found.')
            lesson = module.lessons.filter(title=lesson_title).first()
            if lesson is None:
                raise CommandError(f'Lesson "{lesson_title}" was not found.')
            LessonBlock.objects.update_or_create(
                lesson=lesson,
                position=position,
                defaults={
                    'type': LessonBlock.Type.IMAGE,
                    'content': {'src': src, 'alt': alt},
                    'config': {'label': label},
                    'published': True,
                },
            )
            published += 1

        self.stdout.write(self.style.SUCCESS(
            f'Published {published} illustration blocks for the ML course.'
        ))