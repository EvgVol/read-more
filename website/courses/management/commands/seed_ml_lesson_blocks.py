from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models.course import Course
from courses.models.lesson_block import LessonBlock


def pilot_blocks(lesson, theory):
    return (
        {
            'lesson': lesson,
            'type': LessonBlock.Type.THEORY,
            'position': 10,
            'content': {'markdown': theory},
            'config': {'label': 'Основная теория'},
            'published': True,
        },
        {
            'lesson': lesson,
            'type': LessonBlock.Type.IMAGE,
            'position': 20,
            'content': {
                'src': '/static/images/courses/ml-inzhener/python/01-data-flow.svg',
                'alt': 'Путь данных от входного файла до проверенного результата',
            },
            'config': {'label': 'Схема потока данных'},
            'published': True,
        },
        {
            'lesson': lesson,
            'type': LessonBlock.Type.CODE_EXAMPLE,
            'position': 30,
            'content': {
                'language': 'python',
                'code': (
                    'from pathlib import Path\n\n'
                    'def read_text(path: str) -> str:\n'
                    '    source = Path(path)\n'
                    '    if not source.exists():\n'
                    '        raise FileNotFoundError(source)\n'
                    '    return source.read_text(encoding="utf-8")\n'
                ),
            },
            'config': {'label': 'Минимальный проверяемый загрузчик'},
            'published': True,
        },
        {
            'lesson': lesson,
            'type': LessonBlock.Type.IMAGE,
            'position': 40,
            'content': {
                'src': '/static/images/courses/ml-inzhener/python/03-validation-loop.svg',
                'alt': 'Цикл проверки результата преобразования данных',
            },
            'config': {'label': 'Цикл проверки'},
            'published': True,
        },
        {
            'lesson': lesson,
            'type': LessonBlock.Type.SUMMARY,
            'position': 50,
            'content': {
                'markdown': (
                    '## Итог пилотного урока\n\n'
                    'Перед следующим этапом студент должен уметь:\n\n'
                    '- описать схему входных данных;\n'
                    '- отделить чтение, преобразование и проверку;\n'
                    '- явно обрабатывать ошибки;\n'
                    '- подтвердить результат небольшим `assert`;\n'
                    '- объяснить, почему одинаковый вход даёт воспроизводимый результат.\n\n'
                    ':::self-check\n'
                    'Что произойдёт, если файл существует, но его схема изменилась? '
                    'Где должна находиться эта проверка?\n'
                    ':::'
                ),
            },
            'config': {'label': 'Ключевые выводы'},
            'published': True,
        },
    )


class Command(BaseCommand):
    help = 'Seed the published LessonBlock pilot for the first ML engineer lesson.'

    @transaction.atomic
    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        if course is None:
            raise CommandError('Course "ml-inzhener" does not exist. Run seed_ml_course first.')

        lesson = (
            course.modules.filter(lessons__title='Python для анализа данных')
            .prefetch_related('lessons')
            .first()
        )
        if lesson is None:
            raise CommandError('Pilot lesson "Python для анализа данных" was not found.')
        lesson = lesson.lessons.get(title='Python для анализа данных')
        material = getattr(lesson, 'material', None)
        if material is None or not material.theory.strip():
            raise CommandError('Pilot lesson must have seeded theory before lesson blocks.')

        records = pilot_blocks(lesson, material.theory)
        for record in records:
            position = record.pop('position')
            LessonBlock.objects.update_or_create(
                lesson=record.pop('lesson'),
                position=position,
                defaults=record,
            )

        self.stdout.write(self.style.SUCCESS(
            f'Published {len(records)} lesson blocks for "{lesson.title}".'
        ))
