from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models.course import Course
from courses.models.quiz import QuizQuestion


QUESTIONS = (
    {
        'position': 10,
        'type': QuizQuestion.Type.SINGLE,
        'prompt': 'Что лучше всего описывает контракт входных данных?',
        'options': [
            {'id': 'a', 'text': 'Только имя файла'},
            {'id': 'b', 'text': 'Схема, типы, ограничения и ожидаемый результат'},
            {'id': 'c', 'text': 'Список библиотек проекта'},
        ],
        'correct_answers': ['b'],
        'explanation': 'Контракт фиксирует структуру данных и проверяемые ограничения до обработки.',
    },
    {
        'position': 20,
        'type': QuizQuestion.Type.MULTIPLE,
        'prompt': 'Какие практики делают загрузчик данных воспроизводимым?',
        'options': [
            {'id': 'a', 'text': 'Явная кодировка файла'},
            {'id': 'b', 'text': 'Проверка схемы после чтения'},
            {'id': 'c', 'text': 'Скрытый except Exception: pass'},
            {'id': 'd', 'text': 'Явные входные аргументы функции'},
        ],
        'correct_answers': ['a', 'b', 'd'],
        'explanation': 'Ошибки должны быть видимыми, а вход и проверки — явными.',
    },
    {
        'position': 30,
        'type': QuizQuestion.Type.SHORT,
        'prompt': 'Как называется свойство массива NumPy, описывающее размеры его осей?',
        'options': [],
        'correct_answers': ['shape'],
        'explanation': 'Атрибут shape показывает размер по каждой оси массива.',
    },
)


class Command(BaseCommand):
    help = 'Seed the published quiz for the first ML engineer lesson.'

    @transaction.atomic
    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        if course is None:
            raise CommandError('Course "ml-inzhener" does not exist. Run seed_ml_course first.')
        module = course.modules.filter(title='Python для ML').first()
        lesson = module.lessons.filter(title='Python для анализа данных').first() if module else None
        if lesson is None:
            raise CommandError('Pilot lesson "Python для анализа данных" was not found.')

        for question in QUESTIONS:
            position = question['position']
            QuizQuestion.objects.update_or_create(
                lesson=lesson,
                position=position,
                defaults={**question, 'published': True, 'points': 1},
            )
        self.stdout.write(self.style.SUCCESS(
            f'Published {len(QUESTIONS)} quiz questions for "{lesson.title}".'
        ))
