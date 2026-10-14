from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = (
        'Preview or remove user actions older than the retention window. '
        'Default is a dry run; pass --apply to actually delete. '
        'Intended for cron: python manage.py cleanup_old_actions --apply'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help='Retention window in days (default: ACTIONS_RETENTION_DAYS from settings).',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually delete actions older than the retention window.',
        )

    def handle(self, *args, **options):
        from actions.models import Action  # local import: avoid app-loading cycle

        from django.conf import settings

        days = options['days']
        if days is None:
            days = getattr(settings, 'ACTIONS_RETENTION_DAYS', 90)
        if days < 1:
            self.stderr.write(self.style.ERROR('--days должен быть не меньше 1.'))
            return

        cutoff = timezone.now() - timezone.timedelta(days=days)
        stale = Action.objects.filter(created__lt=cutoff)
        count = stale.count()

        if not options['apply']:
            self.stdout.write(
                f'Предпросмотр: можно удалить {count} действий старше {days} дн. '
                f'(добавьте --apply, чтобы удалить)'
            )
            return

        deleted, _ = stale.delete()
        self.stdout.write(self.style.SUCCESS(
            f'Удалено {deleted} действий старше {days} дн.'
        ))