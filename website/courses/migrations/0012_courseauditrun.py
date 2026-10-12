from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0011_quizquestion_quizattempt_quizanswer_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseAuditRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('passed', models.BooleanField(default=False)),
                ('modules_count', models.PositiveIntegerField(default=0)),
                ('lessons_count', models.PositiveIntegerField(default=0)),
                ('published_questions_count', models.PositiveIntegerField(default=0)),
                ('issues_count', models.PositiveIntegerField(default=0)),
                ('report', models.JSONField(default=dict)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='audit_runs', to='courses.course')),
            ],
            options={
                'verbose_name': 'course audit run',
                'verbose_name_plural': 'course audit runs',
                'ordering': ['-created', '-id'],
            },
        ),
    ]
