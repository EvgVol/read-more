import json
import re

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
RESOURCE_LINK_PATTERN = re.compile(r'\[[^]]+\]\(https?://[^)]+\)')


def _question_issue(prefix, question):
    issues = []
    prompt = question['prompt'].strip()
    explanation = question['explanation'].strip()
    options = question['options'] or []
    correct_answers = question['correct_answers'] or []
    option_ids = [option.get('id') for option in options]

    if len(prompt) < 10:
        issues.append(f'{prefix}: quiz prompt слишком короткий.')
    if len(explanation) < 20:
        issues.append(f'{prefix}: quiz explanation слишком короткий.')
    if question['points'] < 1:
        issues.append(f'{prefix}: quiz points должен быть положительным.')
    if len(option_ids) != len(set(option_ids)):
        issues.append(f'{prefix}: quiz содержит дублирующиеся id вариантов.')
    if any(not option.get('text', '').strip() for option in options):
        issues.append(f'{prefix}: quiz содержит пустой вариант ответа.')

    valid_ids = set(option_ids)
    if question['type'] in {'single', 'multiple'}:
        if len(options) < 3:
            issues.append(f'{prefix}: для {question["type"]} нужно минимум 3 варианта.')
        if not correct_answers:
            issues.append(f'{prefix}: не задан правильный ответ.')
        if not set(correct_answers).issubset(valid_ids):
            issues.append(f'{prefix}: correct_answers ссылается на отсутствующий вариант.')
        if question['type'] == 'single' and len(correct_answers) != 1:
            issues.append(f'{prefix}: single должен иметь ровно один правильный ответ.')
    elif question['type'] == 'short':
        if options:
            issues.append(f'{prefix}: short-вопрос не должен содержать варианты.')
        if not correct_answers:
            issues.append(f'{prefix}: short-вопрос должен иметь эталонный ответ.')

    return issues


def collect_audit_report(course):
    issues = []
    lessons = list(course.modules.prefetch_related('lessons__material').all())
    flat_lessons = [lesson for module in lessons for lesson in module.lessons.all()]
    if len(lessons) != 7:
        issues.append(f'Ожидалось 7 модулей, найдено {len(lessons)}.')
    if len(flat_lessons) != 28:
        issues.append(f'Ожидалось 28 уроков, найдено {len(flat_lessons)}.')

    question_rows = QuizQuestion.objects.filter(
        lesson__module__course=course,
        published=True,
    ).values(
        'lesson_id', 'type', 'prompt', 'options', 'correct_answers',
        'explanation', 'position', 'points',
    )
    questions_by_lesson = {}
    for row in question_rows:
        questions_by_lesson.setdefault(row['lesson_id'], []).append(row)

    lesson_reports = []
    for lesson in flat_lessons:
        material = getattr(lesson, 'material', None)
        prefix = f'{lesson.module.title} / {lesson.title}'
        lesson_issues = []
        material_report = {
            'theory_words': 0,
            'resources_links': 0,
            'practice_words': 0,
            'self_check_questions': 0,
        }
        if material is None:
            lesson_issues.append(f'{prefix}: отсутствует LessonMaterial.')
        else:
            objectives = material.objectives.strip()
            practice = material.practice.strip()
            self_check = material.self_check.strip()
            theory = material.theory
            material_report.update({
                'theory_words': len(theory.split()),
                'resources_links': len(RESOURCE_LINK_PATTERN.findall(material.resources)),
                'practice_words': len(practice.split()),
                'self_check_questions': self_check.count('?'),
            })
            if not objectives:
                lesson_issues.append(f'{prefix}: пустые objectives.')
            if len(practice.split()) < 20:
                lesson_issues.append(f'{prefix}: practice должна содержать минимум 20 слов.')
            if self_check.count('?') < 3:
                lesson_issues.append(f'{prefix}: self_check должна содержать минимум 3 вопроса.')
            if material_report['resources_links'] < 2:
                lesson_issues.append(f'{prefix}: resources должны содержать минимум 2 ссылки.')
            if not 6000 <= material_report['theory_words'] <= 10000:
                lesson_issues.append(
                    f'{prefix}: theory содержит {material_report["theory_words"]} слов, ожидалось 6000–10000.'
                )
            for heading in REQUIRED_HEADINGS:
                if heading not in theory:
                    lesson_issues.append(f'{prefix}: отсутствует раздел {heading}.')

        questions = questions_by_lesson.get(lesson.id, [])
        positions = [question['position'] for question in questions]
        prompts = [question['prompt'].strip().casefold() for question in questions]
        question_types = sorted({question['type'] for question in questions})
        quiz_report = {
            'count': len(questions),
            'types': question_types,
            'positions_unique': len(positions) == len(set(positions)),
            'prompts_unique': len(prompts) == len(set(prompts)),
        }
        if len(questions) < 3:
            lesson_issues.append(f'{prefix}: опубликовано только {len(questions)} quiz-вопросов.')
        if len(set(question_types)) < 3:
            lesson_issues.append(f'{prefix}: quiz не покрывает 3 типа вопросов.')
        if not quiz_report['positions_unique']:
            lesson_issues.append(f'{prefix}: дублируются позиции quiz-вопросов.')
        if not quiz_report['prompts_unique']:
            lesson_issues.append(f'{prefix}: дублируются формулировки quiz-вопросов.')
        for question in questions:
            lesson_issues.extend(_question_issue(f'{prefix} / позиция {question["position"]}', question))

        issues.extend(lesson_issues)
        lesson_reports.append({
            'module': lesson.module.title,
            'module_id': lesson.module_id,
            'lesson': lesson.title,
            'lesson_id': lesson.id,
            'material': material_report,
            'quiz': quiz_report,
            'issues': lesson_issues,
        })

    return {
        'course': course.title,
        'summary': {
            'modules': len(lessons),
            'lessons': len(flat_lessons),
            'published_questions': sum(item['quiz']['count'] for item in lesson_reports),
            'lessons_with_issues': sum(bool(item['issues']) for item in lesson_reports),
            'issues': len(issues),
        },
        'lessons': lesson_reports,
        'issues': issues,
    }


def collect_audit_issues(course):
    return collect_audit_report(course)['issues']


def render_text_report(report):
    lines = [
        f'Отчёт аудита: {report["course"]}',
        (
            f'Итог: {report["summary"]["modules"]} модулей, '
            f'{report["summary"]["lessons"]} уроков, '
            f'{report["summary"]["published_questions"]} quiz-вопросов, '
            f'замечаний: {report["summary"]["issues"]}'
        ),
        '',
    ]
    for lesson in report['lessons']:
        material = lesson['material']
        quiz = lesson['quiz']
        status = 'OK' if not lesson['issues'] else 'ERROR'
        lines.append(
            f'[{status}] {lesson["module"]} / {lesson["lesson"]} — '
            f'теория {material["theory_words"]} слов, '
            f'практика {material["practice_words"]} слов, '
            f'self-check {material["self_check_questions"]} вопросов, '
            f'quiz {quiz["count"]} ({", ".join(quiz["types"])})'
        )
        lines.extend(f'  - {issue}' for issue in lesson['issues'])
    if report['issues']:
        lines.extend(['', 'Аудит не пройден.'])
    else:
        lines.extend(['', 'Аудит пройден.'])
    return '\n'.join(lines)


class Command(BaseCommand):
    help = 'Audit completeness and structure of the ML learning content.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--report',
            action='store_true',
            help='Print per-lesson metrics for course editors.',
        )
        parser.add_argument(
            '--format',
            choices=('text', 'json'),
            default='text',
            help='Report format; json implies --report.',
        )

    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        if course is None:
            raise CommandError('Course "ml-inzhener" does not exist.')

        report = collect_audit_report(course)
        issues = report['issues']
        if options['format'] == 'json':
            self.stdout.write(json.dumps(report, ensure_ascii=False, indent=2))
            if issues:
                raise CommandError('Аудит курса не пройден.')
            return
        if options['report']:
            self.stdout.write(render_text_report(report))
            if issues:
                raise CommandError('Аудит курса не пройден.')
            return
        if issues:
            raise CommandError('Аудит курса не пройден:\n- ' + '\n- '.join(issues))

        question_count = report['summary']['published_questions']
        self.stdout.write(self.style.SUCCESS(
            f'Аудит пройден: 7 модулей, 28 уроков, {question_count} quiz-вопросов.'
        ))
