import re
import unicodedata
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from courses.models.quiz import QuizAnswer, QuizAttempt, QuizQuestion


PASS_THRESHOLD = Decimal('0.80')
_WHITESPACE_RE = re.compile(r'\s+')


def normalize_short_answer(value):
    """Apply the documented default: Unicode NFKC, casefold and collapsed spaces."""
    normalized = unicodedata.normalize('NFKC', str(value or '')).casefold().strip()
    return _WHITESPACE_RE.sub(' ', normalized)


def _as_answers(value):
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return [str(value)]


def _score_question(question, raw_answer):
    submitted = _as_answers(raw_answer)
    correct = _as_answers(question.correct_answers)
    if question.type == QuizQuestion.Type.SHORT:
        normalized = normalize_short_answer(submitted[0] if submitted else '')
        accepted = {normalize_short_answer(item) for item in correct}
        return (Decimal('1') if normalized in accepted else Decimal('0'), normalized, submitted)
    if question.type == QuizQuestion.Type.SINGLE:
        score = Decimal('1') if submitted[:1] == correct[:1] else Decimal('0')
        return score, '', submitted[:1]

    correct_set = set(correct)
    submitted_set = set(submitted)
    if not correct_set:
        return Decimal('0'), '', sorted(submitted_set)
    matched = len(submitted_set & correct_set)
    wrong = len(submitted_set - correct_set)
    score = max(Decimal('0'), Decimal(matched) / len(correct_set) - Decimal(wrong) / len(correct_set))
    return min(Decimal('1'), score), '', sorted(submitted_set)


@transaction.atomic
def submit_quiz(*, user, lesson, answers):
    """Create an immutable attempt and grade only published questions server-side."""
    questions = list(QuizQuestion.objects.filter(lesson=lesson, published=True))
    if not questions:
        raise ValidationError('В этом уроке пока нет опубликованных вопросов.')

    attempt = QuizAttempt.objects.create(
        user=user,
        lesson=lesson,
        total_points=sum(question.points for question in questions),
    )
    earned = Decimal('0')
    for question in questions:
        score, normalized, selected = _score_question(
            question,
            answers.get(str(question.id)),
        )
        awarded = (Decimal(question.points) * score).quantize(Decimal('0.01'))
        is_correct = score == Decimal('1')
        earned += awarded
        QuizAnswer.objects.create(
            attempt=attempt,
            question=question,
            selected_answers=selected,
            normalized_answer=normalized,
            awarded_points=awarded,
            is_correct=is_correct,
            feedback=question.explanation,
        )
    attempt.earned_points = earned
    attempt.passed = earned >= Decimal(attempt.total_points) * PASS_THRESHOLD
    attempt.save(update_fields=['earned_points', 'passed'])
    return attempt


def course_quiz_progress(*, user, course):
    """Summarize the latest attempt for each quiz lesson in a course."""
    lesson_ids = set(
        QuizQuestion.objects.filter(
            lesson__module__course=course,
            published=True,
        ).values_list('lesson_id', flat=True).distinct()
    )
    attempts = QuizAttempt.objects.filter(
        user=user,
        lesson_id__in=lesson_ids,
    ).order_by('lesson_id', '-submitted_at', '-id')
    latest_by_lesson = {}
    for attempt in attempts:
        latest_by_lesson.setdefault(attempt.lesson_id, attempt)
    latest = list(latest_by_lesson.values())
    passed = sum(attempt.passed for attempt in latest)
    average = round(sum(attempt.percent for attempt in latest) / len(latest)) if latest else 0
    return {
        'total_quizzes': len(lesson_ids),
        'attempted_quizzes': len(latest),
        'passed_quizzes': passed,
        'average_percent': average,
    }


def module_quiz_progress(*, user, course):
    """Return the same latest-attempt summary grouped by course module."""
    question_rows = list(
        QuizQuestion.objects.filter(
            lesson__module__course=course,
            published=True,
        ).values_list('lesson_id', 'lesson__module_id')
    )
    lesson_module = {lesson_id: module_id for lesson_id, module_id in question_rows}
    attempts = QuizAttempt.objects.filter(
        user=user,
        lesson_id__in=lesson_module,
    ).order_by('lesson_id', '-submitted_at', '-id')
    latest_by_lesson = {}
    for attempt in attempts:
        latest_by_lesson.setdefault(attempt.lesson_id, attempt)

    result = {}
    for lesson_id, module_id in lesson_module.items():
        summary = result.setdefault(module_id, {
            'total_quizzes': 0,
            'attempted_quizzes': 0,
            'passed_quizzes': 0,
            'average_percent': 0,
            '_percents': [],
        })
        summary['total_quizzes'] += 1
        attempt = latest_by_lesson.get(lesson_id)
        if attempt:
            summary['attempted_quizzes'] += 1
            summary['passed_quizzes'] += int(attempt.passed)
            summary['_percents'].append(attempt.percent)
    for summary in result.values():
        percents = summary.pop('_percents')
        summary['average_percent'] = round(sum(percents) / len(percents)) if percents else 0
    return result
