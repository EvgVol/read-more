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


def single_check(prompt, correct, options, explanation):
    return ({
        'position': 10,
        'type': QuizQuestion.Type.SINGLE,
        'prompt': prompt,
        'options': [
            {'id': key, 'text': text}
            for key, text in zip(('a', 'b', 'c'), options)
        ],
        'correct_answers': [correct],
        'explanation': explanation,
    },)


EXTRA_QUIZZES = {
    'Векторы и матрицы': single_check('Какая форма X соответствует 100 объектам и 5 признакам?', 'b', ('(5, 100)', '(100, 5)', '(100, 100)'), 'В ML-таблице строки — объекты, колонки — признаки.'),
    'Вероятности и распределения': single_check('Что означает P(A|B)?', 'a', ('Вероятность A при условии B', 'Вероятность B при условии A', 'Вероятность A и B всегда'), 'Условная вероятность зависит от известного условия B.'),
    'Статистические оценки': single_check('Какая оценка обычно устойчивее к одному экстремальному выбросу?', 'c', ('Среднее', 'Дисперсия', 'Медиана'), 'Медиана зависит от порядка значений и обычно меньше меняется из-за одного выброса.'),
    'Градиентный спуск': single_check('В какую сторону меняют параметры при минимизации функции?', 'b', ('По градиенту', 'Против градиента', 'Случайно без проверки loss'), 'Градиент указывает направление роста, поэтому шаг минимизации идёт против него.'),
    'EDA: исследовательский анализ': single_check('Что проверяют до обучения модели?', 'a', ('Размер, типы, пропуски и диапазоны данных', 'Только финальную accuracy', 'Только название файла'), 'EDA начинается с происхождения, схемы, качества и ограничений данных.'),
    'Визуализация данных': single_check('Какой график лучше показывает связь двух числовых признаков?', 'b', ('Гистограмма', 'Scatter plot', 'Таблица зависимостей'), 'Scatter plot показывает пары значений и возможную структуру связи.'),
    'Пропуски и выбросы': single_check('На какой части данных нужно обучать imputer?', 'a', ('Только train', 'Только test', 'На train и test вместе'), 'Параметры заполнения должны быть изучены только на train, чтобы избежать leakage.'),
    'Разделение выборок и leakage': single_check('Почему target нельзя использовать при формировании признака до момента предсказания?', 'c', ('Это замедляет обучение', 'Это меняет dtype', 'Это даёт утечку будущей информации'), 'Признак не должен содержать информацию, которая недоступна в момент inference.'),
    'Линейные модели': single_check('Что добавляет bias в линейной модели?', 'a', ('Свободный член', 'Случайность в target', 'Дополнительный train split'), 'Bias позволяет сдвинуть линейную зависимость относительно начала координат.'),
    'Деревья и ансамбли': single_check('Что обычно снижает variance одного дерева?', 'b', ('Увеличение leakage', 'Ансамблирование нескольких деревьев', 'Удаление validation'), 'Ансамбли объединяет несколько моделей и может сделать предсказание устойчивее.'),
    'Классификация и метрики': single_check('Какая метрика одинаково взвешивает классы при усреднении F1?', 'c', ('Micro F1', 'Accuracy', 'Macro F1'), 'Macro F1 считает метрику по каждому классу и усредняет их без учёта размера класса.'),
    'Подбор гиперпараметров': single_check('Где должен находиться preprocessing при cross-validation?', 'a', ('Внутри Pipeline', 'После оценки test', 'В отдельном шаге после всех fold'), 'Pipeline обучает преобразования только на train-части каждого fold.'),
    'Нейронные сети': single_check('Что вычисляет backpropagation?', 'b', ('Новый test split', 'Градиенты параметров по loss', 'Только размер batch'), 'Backpropagation распространяет ошибку назад и вычисляет градиенты.'),
    'PyTorch и тензоры': single_check('Что обычно используют вместе с model.eval() на inference?', 'a', ('torch.no_grad()', 'optimizer.step()', 'loss.backward()'), 'no_grad отключает построение графа градиентов и экономит память.'),
    'Компьютерное зрение': single_check('Какой формат batch изображений обычно использует PyTorch?', 'c', ('[H, W, C, N]', '[N, H, W, C]', '[N, C, H, W]'), 'В torchvision channel dimension обычно идёт перед высотой и шириной.'),
    'Регуляризация и перенос обучения': single_check('Когда dropout отключается?', 'b', ('Только на train', 'На evaluation/inference', 'Никогда'), 'В eval dropout не должен случайно выключать активации.'),
    'Предобработка текста': single_check('На какой выборке строят vocabulary?', 'a', ('Только train', 'Только test', 'На всех данных до split'), 'Иначе статистика test просачивается в обучение.'),
    'Эмбеддинги и трансформеры': single_check('Что делает attention в трансформере?', 'c', ('Удаляет все редкие слова', 'Фиксирует один порядок признаков', 'Взвешивает важность токенов в контексте'), 'Attention строит контекстное взаимодействие между позициями последовательности.'),
    'Классификация текстов': single_check('Какая метрика полезна при равной важности редких и частых классов?', 'b', ('Micro F1', 'Macro F1', 'Только accuracy'), 'Macro F1 не позволяет частому классу полностью скрыть слабый результат редкого класса.'),
    'Рекомендательные системы': single_check('Что делает candidate generation?', 'a', ('Формирует небольшой набор объектов для ранжирования', 'Обучает только tokenizer', 'Удаляет все новые объекты'), 'Сначала система сужает множество кандидатов, затем ranking выбирает порядок.'),
    'FastAPI и сервис модели': single_check('Зачем endpoint /health отделяют от /predict?', 'c', ('Чтобы принимать больше target', 'Чтобы скрыть модель от тестов', 'Чтобы проверять доступность сервиса без инференса'), 'Health check должен быстро показывать состояние сервиса и зависимостей.'),
    'Docker и CI/CD': single_check('Где нельзя хранить секрет в Docker-проекте?', 'b', ('В secret manager', 'В Dockerfile и image layers', 'В runtime secret storage'), 'Секрет в image layer может остаться доступным после удаления строки из Dockerfile.'),
    'Мониторинг и обновление моделей': single_check('Что описывает data drift?', 'a', ('Изменение распределения входных данных', 'Изменение CSS', 'Рост числа unit-тестов'), 'Data drift отслеживает сдвиг входных данных относительно reference-периода.'),
    'Итоговый ML-проект': single_check('Что обязательно должен позволять README итогового проекта?', 'c', ('Только показать скриншот', 'Скрыть версии библиотек', 'Воспроизвести запуск и проверить ограничения'), 'README делает решение продолжимым другим инженером и фиксирует ограничения.'),
}


class Command(BaseCommand):
    help = 'Seed published quizzes for all ML engineer lessons.'

    @transaction.atomic
    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        if course is None:
            raise CommandError('Course "ml-inzhener" does not exist. Run seed_ml_course first.')
        modules = {module.title: module for module in course.modules.prefetch_related('lessons')}
        total = 0
        all_quizzes = {**PYTHON_QUIZZES, **EXTRA_QUIZZES}
        for lesson_title, questions in all_quizzes.items():
            module = next((item for item in modules.values() if item.lessons.filter(title=lesson_title).exists()), None)
            lesson = module.lessons.filter(title=lesson_title).first() if module else None
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
            f'Published {total} quiz questions for the ML engineer course.'
        ))
