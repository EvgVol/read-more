# Generated by Django 4.2.4 on 2023-09-08 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actions', '0002_alter_action_target_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='target_id',
            field=models.PositiveIntegerField(blank=True, default=0),
            preserve_default=False,
        ),
    ]
