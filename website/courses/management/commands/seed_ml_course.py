import os
import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from courses.models.advantage import Advantage
from courses.models.course import Course
from courses.models.content import Content, Text
from courses.models.module import Module
from courses.models.subject import Subject
from courses.models.technology import Technology


class Command(BaseCommand):
    help = 'Create or update the ML engineer course and its catalog data.'

    image_name = 'images/courses/ml-inzhener/hero.png'
    subject_image_name = 'images/subjects/programming.png'
    advantage_image_name = 'images/courses/ml-inzhener/advantages/{index}.png'

    modules = (
        (
            'Python для ML',
            'Базовый Python, структуры данных, функции, ООП и инструменты разработки.',
            ('Python для анализа данных', 'NumPy и векторные вычисления', 'Pandas и подготовка таблиц', 'Git, окружения и Jupyter'),
        ),
        (
            'Математика и статистика',
            'Линейная алгебра, вероятность и статистика, необходимые для понимания моделей.',
            ('Векторы и матрицы', 'Вероятности и распределения', 'Статистические оценки', 'Градиентный спуск'),
        ),
        (
            'Анализ данных',
            'Полный цикл подготовки данных: исследование, визуализация и контроль качества.',
            ('EDA: исследовательский анализ', 'Визуализация данных', 'Пропуски и выбросы', 'Разделение выборок и leakage'),
        ),
        (
            'Классический Machine Learning',
            'Регрессия, классификация, деревья решений и ансамбли с практикой на реальных задачах.',
            ('Линейные модели', 'Деревья и ансамбли', 'Классификация и метрики', 'Подбор гиперпараметров'),
        ),
        (
            'Deep Learning',
            'Нейронные сети и PyTorch: от архитектуры до обучения и отладки моделей.',
            ('Нейронные сети', 'PyTorch и тензоры', 'Компьютерное зрение', 'Регуляризация и перенос обучения'),
        ),
        (
            'NLP и рекомендательные системы',
            'Работа с текстом, эмбеддингами и рекомендациями для прикладных продуктов.',
            ('Предобработка текста', 'Эмбеддинги и трансформеры', 'Классификация текстов', 'Рекомендательные системы'),
        ),
        (
            'MLOps и итоговый проект',
            'Вывод модели в продакшен, мониторинг качества и защита итогового проекта.',
            ('FastAPI и сервис модели', 'Docker и CI/CD', 'Мониторинг и обновление моделей', 'Итоговый ML-проект'),
        ),
    )

    technologies = (
        ('Python', 'https://www.python.org/', 'Основной язык разработки ML-сервисов'),
        ('NumPy', 'https://numpy.org/', 'Векторные и матричные вычисления'),
        ('Pandas', 'https://pandas.pydata.org/', 'Работа с табличными данными'),
        ('Scikit-learn', 'https://scikit-learn.org/', 'Классические алгоритмы машинного обучения'),
        ('PyTorch', 'https://pytorch.org/', 'Обучение нейронных сетей'),
        ('SQL', 'https://www.postgresql.org/docs/current/sql.html', 'Получение и подготовка данных'),
        ('Docker', 'https://www.docker.com/', 'Упаковка и запуск ML-сервисов'),
    )

    advantages = (
        'Практика на реальных наборах данных',
        '7 последовательных модулей от базы до MLOps',
        'Итоговый проект в портфолио',
        'Навыки для запуска модели в продакшен',
    )

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        owner = User.objects.order_by('id').first()
        if owner is None:
            owner = User.objects.create_user(
                username='ml-course-admin',
                email='ml-course-admin@read-more.local',
                password=None,
            )

        image_path = Path(__file__).resolve().parents[3] / 'static' / self.image_name
        if not image_path.exists():
            raise FileNotFoundError(f'Course image not found: {image_path}')
        subject_image_path = (
            Path(__file__).resolve().parents[3] / 'static' / self.subject_image_name
        )
        if not subject_image_path.exists():
            raise FileNotFoundError(f'Subject image not found: {subject_image_path}')

        subject, _ = Subject.objects.update_or_create(
            slug='programmirovanie',
            defaults={
                'title': 'Программирование',
                'description': 'Разработка и инженерные технологии',
            },
        )
        self.replace_image(
            subject, subject_image_path, 'programming.png',
            thumbnails=(('500x333', {'crop': 'center'}),),
        )

        technology_objects = []
        for name, url, hints in self.technologies:
            technology, _ = Technology.objects.update_or_create(
                name=name,
                defaults={'url': url, 'hints': hints},
            )
            technology_objects.append(technology)

        advantage_objects = []
        for index, name in enumerate(self.advantages, start=1):
            advantage, _ = Advantage.objects.update_or_create(name=name, defaults={})
            advantage_image_path = (
                Path(__file__).resolve().parents[3]
                / 'static' / self.advantage_image_name.format(index=index)
            )
            if not advantage_image_path.exists():
                raise FileNotFoundError(f'Advantage image not found: {advantage_image_path}')
            self.replace_image(
                advantage, advantage_image_path, f'ml-advantage-{index}.png',
                thumbnails=(('100x100', {'crop': 'center', 'upscale': True}),),
            )
            advantage_objects.append(advantage)

        course, _ = Course.objects.update_or_create(
            slug='ml-inzhener',
            defaults={
                'owner': owner,
                'subject': subject,
                'complexity': Course.Complexity.MIDDLE,
                'description': (
                    'Освойте профессию ML-инженера: научитесь готовить данные, '
                    'обучать модели машинного обучения и запускать их в продакшен.'
                ),
                'title': 'ML-инженер',
                'overview': 'Машинное обучение от Python до MLOps',
                'load': Course.Load.MODERATE,
                'period': 8,
                'count_projects': 4,
            },
        )
        self.replace_image(
            course, image_path, 'ml-engineer.png',
            thumbnails=(('600x370', {'crop': 'center'}),),
        )
        course.technologies.set(technology_objects)
        course.advantages.set(advantage_objects)
        course.students.add(owner)

        for old_module in course.modules.all():
            for old_content in old_module.contents.all():
                item = old_content.item
                old_content.delete()
                if isinstance(item, Text) and item.title.startswith('Материал модуля:'):
                    item.delete()
        for module_order, (title, description, lessons) in enumerate(self.modules, start=1):
            module, _ = Module.objects.update_or_create(
                course=course,
                title=title,
                defaults={
                    'description': description,
                    'order': module_order,
                },
            )
            for lesson_order, lesson_title in enumerate(lessons, start=1):
                module.lessons.update_or_create(
                    title=lesson_title,
                    defaults={'order': lesson_order},
                )
            text = Text.objects.create(
                owner=owner,
                title=f'Материал модуля: {title}',
                content=(
                    f'{description}\n\n'
                    'В этом модуле вы последовательно разберёте:\n'
                    + '\n'.join(f'• {lesson}' for lesson in lessons)
                    + '\n\nПосле изучения модуля закрепите материал практическим заданием '
                    'и сохраните результат в портфолио.'
                ),
            )
            Content.objects.create(
                module=module,
                content_type=ContentType.objects.get_for_model(Text),
                object_id=text.pk,
                order=1,
            )

        self.stdout.write(self.style.SUCCESS(
            f'Course "{course.title}" created/updated: '
            f'{course.modules.count()} modules, '
            f'{sum(module.lessons.count() for module in course.modules.all())} lessons.'
        ))

    @staticmethod
    def replace_image(instance, source_path, target_name, thumbnails=()):
        """Replace the instance image with a deterministic file name.

        The previous file, any file already occupying the target name, and any
        orphaned auto-suffixed copies (e.g. ``ml-engineer_1a2b3c4d.png`` left
        behind by older Django saves) are removed first so the media volume
        never accumulates duplicate gray placeholders. ``thumbnails`` is a tuple
        of ``(geometry, options)`` for the sizes the templates request; each is
        pre-generated so the file exists at deploy time instead of 404-ing on
        the first render.
        """
        field = instance.image.field
        old = instance.image
        if old and old.name:
            old_file = getattr(old, 'path', None)
            if old_file and os.path.exists(old_file):
                os.remove(old_file)
            old.delete(save=False)

        upload_to = field.upload_to
        if callable(upload_to):
            upload_to = upload_to(instance, target_name)
        target_dir = os.path.join(settings.MEDIA_ROOT, *upload_to.split('/'))
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, target_name)
        if os.path.exists(target_file):
            os.remove(target_file)
        Command._purge_orphaned_images(field, instance, target_dir, target_name)

        with source_path.open('rb') as image_file:
            instance.image.save(target_name, File(image_file), save=False)
        instance.save()

        # sorl-thumbnail keys its cache (kvstore rows + files) by the source
        # file name, not by content or mtime, so a thumbnail of the old
        # placeholder would keep being served after the force-replace (or
        # 404 if its file was deleted). Drop every cached derivative of the
        # replaced image; the next render regenerates it from the new file.
        from sorl.thumbnail import delete as sorl_delete
        try:
            sorl_delete(instance.image, delete_file=False)
        except Exception:  # noqa: BLE001 - cache purging must never break seeding
            pass

        # Pre-generate the exact sizes the templates request. sorl paths are
        # deterministic (md5 of source name + geometry + options), so the files
        # land where the templates reference them and the landing page has no
        # 404 window after a redeploy.
        from sorl.thumbnail import get_thumbnail
        for geometry, options in thumbnails:
            try:
                get_thumbnail(instance.image, geometry, **options)
            except Exception:  # noqa: BLE001 - pre-generation is best-effort
                pass

    @staticmethod
    def _purge_orphaned_images(field, instance, target_dir, target_name):
        """Delete suffixed copies of ``target_name`` not referenced in the DB.

        Django's FileField appends ``_<random>`` before the extension when a
        same-named file already exists, so an orphan of ``ml-engineer.png`` is
        ``ml-engineer_ABCD1234.png``. Match on stem plus an optional suffix.
        """
        stem, ext = os.path.splitext(target_name)
        pattern = re.compile(
            rf'^{re.escape(stem)}(_[A-Za-z0-9]+)?{re.escape(ext)}$'
        )
        model = instance.__class__
        referenced = set(
            model.objects.exclude(pk=instance.pk).values_list(
                f'{field.name}', flat=True
            )
        )
        referenced = {name for name in referenced if name}
        for entry in os.scandir(target_dir):
            if not entry.is_file() or not pattern.fullmatch(entry.name):
                continue
            if entry.name == target_name:
                continue
            stored = os.path.relpath(entry.path, settings.MEDIA_ROOT)
            if stored in referenced:
                continue
            os.remove(entry.path)
