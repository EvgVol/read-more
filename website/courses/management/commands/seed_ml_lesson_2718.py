from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.management.commands.lesson_2718_content import QUIZ, blocks_for_lesson
from courses.models.course import Course
from courses.models.lesson_block import LessonBlock
from courses.models.quiz import QuizQuestion


class Command(BaseCommand):
    help = 'Publish Iteration 2 blocks and quiz for lesson 2718 only.'

    @transaction.atomic
    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        module = course.modules.filter(title='Python для ML').first() if course else None
        lesson = module.lessons.filter(title='NumPy и векторные вычисления').first() if module else None
        if lesson is None:
            raise CommandError('Lesson "NumPy и векторные вычисления" was not found.')
        LessonBlock.objects.filter(lesson=lesson).delete()
        for block in blocks_for_lesson(lesson):
            LessonBlock.objects.create(**block)
        positions = []
        for question in QUIZ:
            positions.append(question['position'])
            QuizQuestion.objects.update_or_create(lesson=lesson, position=question['position'], defaults={**question, 'published': True, 'points': 1})
        QuizQuestion.objects.filter(lesson=lesson).exclude(position__in=positions).delete()
        self.stdout.write(self.style.SUCCESS(f'Published Iteration 2 content for lesson {lesson.id}: {len(positions)} questions.'))
