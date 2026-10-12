from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_remove_course_price_immediately_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LessonMaterial',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'objectives',
                    models.TextField(blank=True, verbose_name='learning objectives'),
                ),
                (
                    'theory',
                    models.TextField(blank=True, verbose_name='theory'),
                ),
                (
                    'practice',
                    models.TextField(blank=True, verbose_name='practice'),
                ),
                (
                    'self_check',
                    models.TextField(blank=True, verbose_name='self-check'),
                ),
                (
                    'resources',
                    models.TextField(blank=True, verbose_name='resources'),
                ),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
                (
                    'lesson',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='material',
                        to='courses.lesson',
                        verbose_name='lesson',
                    ),
                ),
            ],
            options={
                'verbose_name': 'lesson material',
                'verbose_name_plural': 'lesson materials',
                'ordering': ['lesson__module__order', 'lesson__order'],
            },
        ),
    ]
