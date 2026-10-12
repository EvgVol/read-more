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
