# Generated by Django 4.2.1 on 2023-08-17 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_module_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='module',
            name='image',
        ),
    ]
