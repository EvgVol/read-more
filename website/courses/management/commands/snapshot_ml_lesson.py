import hashlib
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from courses.models.course import Course
from courses.models.lesson_block import LessonBlock
from courses.models.lesson_material import LessonMaterial
from courses.models.quiz import QuizQuestion


def lesson_payload(lesson):
    material = LessonMaterial.objects.filter(lesson=lesson).values(
        'objectives', 'theory', 'practice', 'self_check', 'resources', 'updated'
    ).first()
    if material and material['updated']:
        material['updated'] = material['updated'].isoformat()
    return {
        'lesson': {'id': lesson.id, 'title': lesson.title, 'module_id': lesson.module_id},
        'material': material,
        'blocks': list(LessonBlock.objects.filter(lesson=lesson).values(
            'id', 'type', 'position', 'schema_version', 'content', 'config', 'published',
        )),
        'quiz': list(QuizQuestion.objects.filter(lesson=lesson).values(
            'id', 'type', 'position', 'prompt', 'options', 'correct_answers',
            'explanation', 'metadata', 'points', 'published',
        )),
    }


class Command(BaseCommand):
    help = 'Write a JSON snapshot of lesson 2717 content for restore.'

    def add_arguments(self, parser):
        parser.add_argument('path', type=Path)

    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        lesson = course.modules.filter(title='Python для ML').first().lessons.filter(
            title='Python для анализа данных'
        ).first() if course else None
        if lesson is None:
            raise CommandError('Reference lesson was not found.')
        payload = lesson_payload(lesson)
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode()
        snapshot = {
            'format': 1,
            'sha256': hashlib.sha256(encoded).hexdigest(),
            'content': payload,
        }
        options['path'].parent.mkdir(parents=True, exist_ok=True)
        options['path'].write_text(
            json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2) + '\n',
            encoding='utf-8',
        )
        self.stdout.write(self.style.SUCCESS(
            f'Snapshot written: {options["path"]} ({snapshot["sha256"]})'
        ))
