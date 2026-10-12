from django.core.management.base import BaseCommand, CommandError

from courses.models.course import Course
from courses.models.quiz import QuizQuestion


REQUIRED_HEADINGS = (
    '## Интуиция',
    '## Базовые понятия',
    '## Пошаговый разбор',
    '## Практические примеры',
    '## Типичные ошибки',
    '## Связь с ML-инженерией',
    '## Итоги',
)


def collect_audit_issues(course):
    issues = []
    lessons = list(
        course.modules.prefetch_related('lessons__material').all()
    )
    flat_lessons = [lesson for module in lessons for lesson in module.lessons.all()]
    if len(lessons) != 7:
        issues.append(f'Ожидалось 7 модулей, найдено {len(lessons)}.')
    if len(flat_lessons) != 28:
        issues.append(f'Ожидалось 28 уроков, найдено {len(flat_lessons)}.')

    question_rows = QuizQuestion.objects.filter(
        lesson__module__course=course,
        published=True,
    ).values('lesson_id', 'type', 'prompt', 'position')
    questions_by_lesson = {}
    for row in question_rows:
        questions_by_lesson.setdefault(row['lesson_id'], []).append(row)

    for lesson in flat_lessons:
        material = getattr(lesson, 'material', None)
        prefix = f'{lesson.module.title} / {lesson.title}'
        if material is None:
            issues.append(f'{prefix}: отсутствует LessonMaterial.')
            continue
        if not material.objectives.strip():
            issues.append(f'{prefix}: пустые objectives.')
        if not material.practice.strip():
            issues.append(f'{prefix}: пустая practice.')
        if not material.self_check.strip():
            issues.append(f'{prefix}: пустая self_check.')
        words = material.theory.split()
        if not 6000 <= len(words) <= 10000:
            issues.append(f'{prefix}: theory содержит {len(words)} слов, ожидалось 6000–10000.')
        for heading in REQUIRED_HEADINGS:
            if heading not in material.theory:
                issues.append(f'{prefix}: отсутствует раздел {heading}.')

        questions = questions_by_lesson.get(lesson.id, [])
        if len(questions) < 3:
            issues.append(f'{prefix}: опубликовано только {len(questions)} quiz-вопросов.')
        if len({question['type'] for question in questions}) < 3:
            issues.append(f'{prefix}: quiz не покрывает 3 типа вопросов.')
        positions = [question['position'] for question in questions]
        if len(positions) != len(set(positions)):
            issues.append(f'{prefix}: дублируются позиции quiz-вопросов.')
        prompts = [question['prompt'].strip().casefold() for question in questions]
        if len(prompts) != len(set(prompts)):
            issues.append(f'{prefix}: дублируются формулировки quiz-вопросов.')

    return issues


class Command(BaseCommand):
    help = 'Audit completeness and structure of the ML learning content.'

    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        if course is None:
            raise CommandError('Course "ml-inzhener" does not exist.')

        issues = collect_audit_issues(course)
        if issues:
            raise CommandError('Аудит курса не пройден:\n- ' + '\n- '.join(issues))

        question_count = QuizQuestion.objects.filter(
            lesson__module__course=course,
            published=True,
        ).count()
        self.stdout.write(self.style.SUCCESS(
            f'Аудит пройден: 7 модулей, 28 уроков, {question_count} quiz-вопросов.'
        ))
