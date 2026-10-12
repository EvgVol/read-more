from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0008_lessonmaterial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('not_started', 'Не начат'), ('in_progress', 'В процессе'), ('completed', 'Завершён')], default='not_started', max_length=20)),
                ('current_step', models.PositiveSmallIntegerField(default=1)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('last_opened_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progress_records', to='courses.lesson')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_progress', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['-updated']},
        ),
        migrations.CreateModel(
            name='LessonProgressEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('started', 'Урок начат'), ('section_completed', 'Этап завершён'), ('lesson_completed', 'Урок завершён'), ('reopened', 'Урок открыт повторно')], max_length=24)),
                ('step', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('progress', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='courses.lessonprogress')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['progress', 'created_at'], name='courses_les_progres_1615f3_idx'),
                    models.Index(fields=['event_type', 'created_at'], name='courses_les_event_t_c0eb7e_idx'),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name='lessonprogressevent',
            constraint=models.CheckConstraint(
                check=models.Q(('step__isnull', True), models.Q(('step__gte', 1), ('step__lte', 5)), _connector='OR'),
                name='lesson_progress_event_step_1_to_5',
            ),
        ),
        migrations.AddIndex(
            model_name='lessonprogress',
            index=models.Index(fields=['user', 'status'], name='courses_les_user_id_439b3a_idx'),
        ),
        migrations.AddIndex(
            model_name='lessonprogress',
            index=models.Index(fields=['lesson', 'status'], name='courses_les_lesson__30e92d_idx'),
        ),
        migrations.AddConstraint(
            model_name='lessonprogress',
            constraint=models.UniqueConstraint(fields=('user', 'lesson'), name='unique_lesson_progress_user_lesson'),
        ),
        migrations.AddConstraint(
            model_name='lessonprogress',
            constraint=models.CheckConstraint(
                check=models.Q(('current_step__gte', 1), ('current_step__lte', 5)),
                name='lesson_progress_step_1_to_5',
            ),
        ),
    ]
