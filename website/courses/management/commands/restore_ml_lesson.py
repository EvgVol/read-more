import hashlib
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.models.course import Course
from courses.models.lessons import Lesson
from courses.models.lesson_block import LessonBlock
from courses.models.lesson_material import LessonMaterial
from courses.models.quiz import QuizQuestion


class Command(BaseCommand):
    help = 'Restore lesson content from a snapshot without touching progress.'

    def add_arguments(self, parser):
        parser.add_argument('path', type=Path)

    @transaction.atomic
    def handle(self, *args, **options):
        path = options['path']
        try:
            snapshot = json.loads(path.read_text(encoding='utf-8'))
            payload = snapshot['content']
        except (OSError, ValueError, KeyError) as error:
            raise CommandError(f'Invalid snapshot: {error}') from error
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode()
        if hashlib.sha256(encoded).hexdigest() != snapshot.get('sha256'):
            raise CommandError('Snapshot checksum does not match.')

        course = Course.objects.filter(slug='ml-inzhener').first()
        lesson = Lesson.objects.filter(
            pk=payload['lesson']['id'],
            module__course=course,
            title=payload['lesson']['title'],
        ).first() if course else None
        if lesson is None:
            raise CommandError('Snapshot lesson is not present in the current course.')

        material_data = payload.get('material')
        if material_data:
            material_data = {key: value for key, value in material_data.items() if key != 'updated'}
            LessonMaterial.objects.update_or_create(lesson=lesson, defaults=material_data)

        LessonBlock.objects.filter(lesson=lesson).delete()
        for block in payload.get('blocks', []):
            LessonBlock.objects.create(
                id=block['id'], lesson=lesson, type=block['type'], position=block['position'],
                schema_version=block['schema_version'], content=block['content'],
                config=block['config'], published=block['published'],
            )
        QuizQuestion.objects.filter(lesson=lesson).delete()
        for question in payload.get('quiz', []):
            QuizQuestion.objects.create(
                id=question['id'], lesson=lesson, type=question['type'], position=question['position'],
                prompt=question['prompt'], options=question['options'],
                correct_answers=question['correct_answers'], explanation=question['explanation'],
                metadata=question.get('metadata', {}), points=question['points'],
                published=question['published'],
            )
        self.stdout.write(self.style.SUCCESS(f'Restored lesson {lesson.id}; progress was not modified.'))
