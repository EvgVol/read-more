from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0012_courseauditrun'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizquestion',
            name='metadata',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
