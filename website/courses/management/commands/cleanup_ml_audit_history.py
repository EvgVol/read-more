from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError

from courses.models.audit import CourseAuditRun


class Command(BaseCommand):
    help = 'Preview or remove old saved ML course audit runs.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--keep',
            type=int,
            default=30,
            help='Number of newest runs to keep per course (default: 30).',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually delete runs beyond the retention limit.',
        )

    def handle(self, *args, **options):
        keep = options['keep']
        if keep < 1:
            raise CommandError('--keep должен быть не меньше 1.')

        retained_by_course = defaultdict(int)
        stale_ids = []
        for run_id, course_id in CourseAuditRun.objects.order_by(
            'course_id', '-created', '-id'
        ).values_list('id', 'course_id'):
            if retained_by_course[course_id] < keep:
                retained_by_course[course_id] += 1
            else:
                stale_ids.append(run_id)

        if not options['apply']:
            self.stdout.write(
                f'Предпросмотр: можно удалить {len(stale_ids)} старых запусков. '
                f'Лимит хранения: {keep} на курс.'
            )
            return

        deleted, _ = CourseAuditRun.objects.filter(id__in=stale_ids).delete()
        self.stdout.write(self.style.SUCCESS(
            f'Удалено {deleted} записей аудита. Лимит хранения: {keep} на курс.'
        ))
