from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models.course import Course
from courses.models.lesson_block import LessonBlock


PYTHON_LESSONS = {
    'NumPy и векторные вычисления': {
        'code': 'X = np.asarray(rows, dtype=float)\nmean = X.mean(axis=0)\nstd = X.std(axis=0)\nX_scaled = (X - mean) / np.where(std == 0, 1, std)',
        'summary': 'Проверяйте shape, dtype и axis до вычисления; фиксируйте seed; не смешивайте поэлементное `*` и матричное `@` умножение.',
    },
    'Pandas и подготовка таблиц': {
        'code': 'orders["created_at"] = pd.to_datetime(orders["created_at"], utc=True)\nresult = users.merge(orders, on="user_id", how="left", validate="one_to_many")',
        'summary': 'Перед merge проверяйте ключи, типы и размер результата; после каждого преобразования фиксируйте инвариант, который должен сохраниться.',
    },
    'Git, окружения и Jupyter': {
        'code': 'python -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt\npip freeze > requirements-lock.txt',
        'summary': 'Исследование в notebook удобно, но воспроизводимый pipeline должен жить в коде, иметь зафиксированные зависимости и понятную команду запуска.',
    },
}


def blocks_for_lesson(lesson, material, blueprint):
    return (
        {
            'type': LessonBlock.Type.THEORY,
            'position': 10,
            'content': {'markdown': material.theory},
            'config': {'label': 'Основная теория'},
        },
        {
            'type': LessonBlock.Type.CODE_EXAMPLE,
            'position': 20,
            'content': {'language': 'python', 'code': blueprint['code']},
            'config': {'label': 'Короткий технический пример'},
        },
        {
            'type': LessonBlock.Type.SUMMARY,
            'position': 30,
            'content': {
                'markdown': (
                    '## Итог\n\n'
                    f"{blueprint['summary']}\n\n"
                    ':::self-check\n'
                    'Какой инвариант вы проверите сразу после выполнения этого примера?\n'
                    ':::'
                ),
            },
            'config': {'label': 'Ключевые выводы'},
        },
    )


class Command(BaseCommand):
    help = 'Seed published LessonBlocks for the remaining Python module lessons.'

    @transaction.atomic
    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        if course is None:
            raise CommandError('Course "ml-inzhener" does not exist. Run seed_ml_course first.')

        module = course.modules.filter(title='Python для ML').first()
        if module is None:
            raise CommandError('Module "Python для ML" was not found.')

        published = 0
        for title, blueprint in PYTHON_LESSONS.items():
            lesson = module.lessons.filter(title=title).first()
            if lesson is None:
                raise CommandError(f'Lesson "{title}" was not found.')
            material = getattr(lesson, 'material', None)
            if material is None or not material.theory.strip():
                raise CommandError(f'Lesson "{title}" has no seeded theory.')
            for record in blocks_for_lesson(lesson, material, blueprint):
                position = record.pop('position')
                LessonBlock.objects.update_or_create(
                    lesson=lesson,
                    position=position,
                    defaults={**record, 'published': True},
                )
                published += 1

        self.stdout.write(self.style.SUCCESS(
            f'Published {published} lesson blocks for the Python module.'
        ))
