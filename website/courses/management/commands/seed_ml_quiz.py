from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models.course import Course
from courses.models.quiz import QuizQuestion


PYTHON_QUIZZES = {
    'Python для анализа данных': (
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
    }),
    'NumPy и векторные вычисления': (
        {
            'position': 10,
            'type': QuizQuestion.Type.SINGLE,
            'prompt': 'Какая операция выполняет матричное умножение в NumPy?',
            'options': [
                {'id': 'a', 'text': '*'},
                {'id': 'b', 'text': '@'},
                {'id': 'c', 'text': '//'},
            ],
            'correct_answers': ['b'],
            'explanation': 'Оператор @ используется для матричного умножения, а * — поэлементного.',
        },
        {
            'position': 20,
            'type': QuizQuestion.Type.MULTIPLE,
            'prompt': 'Что нужно проверить перед векторным вычислением?',
            'options': [
                {'id': 'a', 'text': 'shape'},
                {'id': 'b', 'text': 'dtype'},
                {'id': 'c', 'text': 'Цвет терминала'},
                {'id': 'd', 'text': 'axis'},
            ],
            'correct_answers': ['a', 'b', 'd'],
            'explanation': 'Форма, тип и выбранная ось определяют корректность и смысл операции.',
        },
        {
            'position': 30,
            'type': QuizQuestion.Type.SHORT,
            'prompt': 'Как называется механизм согласования совместимых форм массивов?',
            'options': [],
            'correct_answers': ['broadcasting'],
            'explanation': 'Broadcasting позволяет выполнять операции над совместимыми формами без ручного копирования.',
        },
    ),
    'Pandas и подготовка таблиц': (
        {
            'position': 10,
            'type': QuizQuestion.Type.SINGLE,
            'prompt': 'Какой join сохраняет все строки левой таблицы?',
            'options': [
                {'id': 'a', 'text': 'inner'},
                {'id': 'b', 'text': 'left'},
                {'id': 'c', 'text': 'cross'},
            ],
            'correct_answers': ['b'],
            'explanation': 'left join сохраняет строки левой таблицы, даже если совпадения справа нет.',
        },
        {
            'position': 20,
            'type': QuizQuestion.Type.MULTIPLE,
            'prompt': 'Какие проверки полезны до merge таблиц?',
            'options': [
                {'id': 'a', 'text': 'Типы ключей'},
                {'id': 'b', 'text': 'Дубли ключей'},
                {'id': 'c', 'text': 'Размер результата'},
                {'id': 'd', 'text': 'Случайный цвет графика'},
            ],
            'correct_answers': ['a', 'b', 'c'],
            'explanation': 'Типы, уникальность и размер результата помогают обнаружить ошибочное объединение.',
        },
        {
            'position': 30,
            'type': QuizQuestion.Type.SHORT,
            'prompt': 'Как называется табличная структура Pandas с индексом и колонками?',
            'options': [],
            'correct_answers': ['dataframe', 'data frame'],
            'explanation': 'DataFrame хранит двумерные данные, их индекс и типы колонок.',
        },
    ),
    'Git, окружения и Jupyter': (
        {
            'position': 10,
            'type': QuizQuestion.Type.SINGLE,
            'prompt': 'Зачем проекту виртуальное окружение?',
            'options': [
                {'id': 'a', 'text': 'Чтобы изолировать зависимости проекта'},
                {'id': 'b', 'text': 'Чтобы ускорить интернет'},
                {'id': 'c', 'text': 'Чтобы заменить систему контроля версий'},
            ],
            'correct_answers': ['a'],
            'explanation': 'Virtualenv отделяет зависимости проекта от системного Python и других проектов.',
        },
        {
            'position': 20,
            'type': QuizQuestion.Type.MULTIPLE,
            'prompt': 'Что повышает воспроизводимость исследования?',
            'options': [
                {'id': 'a', 'text': 'Зафиксированные зависимости'},
                {'id': 'b', 'text': 'README с командой запуска'},
                {'id': 'c', 'text': 'Скрытое состояние notebook'},
                {'id': 'd', 'text': 'Вынесение устойчивой логики в .py'},
            ],
            'correct_answers': ['a', 'b', 'd'],
            'explanation': 'Другой инженер должен понимать версии, команду запуска и явный источник логики.',
        },
        {
            'position': 30,
            'type': QuizQuestion.Type.SHORT,
            'prompt': 'Как называется система контроля версий, используемая в уроке?',
            'options': [],
            'correct_answers': ['git'],
            'explanation': 'Git хранит историю изменений и помогает работать с атомарными коммитами.',
        },
    ),
}


class Command(BaseCommand):
    help = 'Seed published quizzes for the Python module lessons.'

    @transaction.atomic
    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        if course is None:
            raise CommandError('Course "ml-inzhener" does not exist. Run seed_ml_course first.')
        module = course.modules.filter(title='Python для ML').first()
        if module is None:
            raise CommandError('Module "Python для ML" was not found.')

        total = 0
        for lesson_title, questions in PYTHON_QUIZZES.items():
            lesson = module.lessons.filter(title=lesson_title).first()
            if lesson is None:
                raise CommandError(f'Lesson "{lesson_title}" was not found.')
            for question in questions:
                QuizQuestion.objects.update_or_create(
                    lesson=lesson,
                    position=question['position'],
                    defaults={**question, 'published': True, 'points': 1},
                )
                total += 1
        self.stdout.write(self.style.SUCCESS(
            f'Published {total} quiz questions for the Python module.'
        ))
