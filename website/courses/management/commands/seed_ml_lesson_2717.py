from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from courses.management.commands.lesson_2717_content import (
    PRACTICE,
    QUIZ,
    SUMMARY,
    full_theory,
    section_blocks,
)
from courses.models.course import Course
from courses.models.lesson_block import LessonBlock
from courses.models.lesson_material import LessonMaterial
from courses.models.quiz import QuizQuestion


class Command(BaseCommand):
    help = 'Publish the Iteration 1 reference content for lesson 2717 only.'

    @transaction.atomic
    def handle(self, *args, **options):
        course = Course.objects.filter(slug='ml-inzhener').first()
        if course is None:
            raise CommandError('Course "ml-inzhener" does not exist.')
        module = course.modules.filter(title='Python для ML').first()
        lesson = module.lessons.filter(title='Python для анализа данных').first() if module else None
        if lesson is None or lesson.title != 'Python для анализа данных':
            raise CommandError('Lesson 2717 "Python для анализа данных" was not found.')

        material, _ = LessonMaterial.objects.get_or_create(lesson=lesson)
        material.objectives = 'Определять контракт CSV; строить функции чтения, валидации и обработки; писать тесты; диагностировать ошибки.'
        material.theory = full_theory()
        material.practice = PRACTICE
        material.self_check = SUMMARY
        material.resources = (
            '[Python Tutorial](https://docs.python.org/3/tutorial/)\n'
            '[csv module](https://docs.python.org/3/library/csv.html)\n'
            '[decimal module](https://docs.python.org/3/library/decimal.html)\n'
            '[pytest documentation](https://docs.pytest.org/en/stable/)'
        )
        material.save()

        LessonBlock.objects.filter(lesson=lesson).delete()
        for record in section_blocks(lesson):
            LessonBlock.objects.create(**record)

        positions = []
        for question in QUIZ:
            positions.append(question['position'])
            QuizQuestion.objects.update_or_create(
                lesson=lesson,
                position=question['position'],
                defaults={**question, 'published': True, 'points': 1},
            )
        QuizQuestion.objects.filter(lesson=lesson).exclude(position__in=positions).delete()

        self.stdout.write(self.style.SUCCESS(
            f'Published Iteration 1 content for lesson {lesson.pk}: '
            f'{len(section_blocks(lesson))} blocks and {len(QUIZ)} questions.'
        ))
