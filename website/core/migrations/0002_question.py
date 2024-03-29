# Generated by Django 4.2.4 on 2023-08-31 10:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(help_text='Enter your first name', max_length=50, verbose_name='first name')),
                ('email', models.EmailField(help_text='Enter your email adress', max_length=150, verbose_name='email')),
                ('content', models.TextField(help_text='Post your question', verbose_name='content')),
                ('time_create', models.DateTimeField(auto_now_add=True, verbose_name='time created')),
            ],
            options={
                'verbose_name': 'question',
                'verbose_name_plural': 'questions',
                'ordering': ['-time_create'],
            },
        ),
    ]
