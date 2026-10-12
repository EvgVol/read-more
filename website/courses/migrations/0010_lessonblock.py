from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_lessonprogress_lessonprogressevent_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=32, verbose_name='type')),
                ('position', models.PositiveIntegerField(default=10, verbose_name='position')),
                ('schema_version', models.PositiveSmallIntegerField(default=1, verbose_name='schema version')),
                ('content', models.JSONField(blank=True, default=dict, verbose_name='content')),
                ('config', models.JSONField(blank=True, default=dict, verbose_name='configuration')),
                ('published', models.BooleanField(default=False, verbose_name='published')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='courses.lesson', verbose_name='lesson')),
            ],
            options={
                'verbose_name': 'lesson block',
                'verbose_name_plural': 'lesson blocks',
                'ordering': ['position', 'id'],
                'indexes': [
                    models.Index(fields=['lesson', 'published', 'position'], name='courses_les_lesson__bab0df_idx'),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name='lessonblock',
            constraint=models.UniqueConstraint(fields=('lesson', 'position'), name='unique_lesson_block_position'),
        ),
    ]
