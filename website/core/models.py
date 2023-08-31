from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class PolicyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Policy.Status.CURRENT)


class Policy(models.Model):
    """
    Модель политики конфиденциальности 
    и обработки персональных данных пользователей.
    """

    class Status(models.TextChoices):
        INVALID = 'IN', 'Недействующая'
        CURRENT = 'CR', 'Действующая'

    body = models.TextField("Текст")
    slug = models.SlugField('Slug',
                            max_length=50,
                            unique_for_date='publish')
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    publish = models.DateTimeField('Дата публикации', default=timezone.now)
    updated = models.DateTimeField('Дата изменения', auto_now=True)
    status = models.CharField('Статус',
                            max_length=2,
                            choices=Status.choices,
                            default=Status.INVALID)
    objects = models.Manager()
    published = PolicyManager()


    class Meta:
        ordering = ['-publish']
        verbose_name = 'Политика конфиденциальности'
        verbose_name_plural = 'Политика конфиденциальности'
        indexes = [
            models.Index(fields=['-publish']),
        ]

    def __str__(self):
        return self.body


class Question(models.Model):

    first_name = models.CharField(_("first name"), max_length=50, blank=False,
                                  help_text='Enter your first name')
    email = models.EmailField(_("email"), max_length=150, blank=False,
                              help_text='Enter your email adress')
    content = models.TextField(_("content"), blank=False,
                               help_text='Post your question')
    time_create = models.DateTimeField(_("time created"), auto_now_add=True)
    
    class Meta:
        ordering = ['-time_create']
        verbose_name = _("question")
        verbose_name_plural = _("questions")

    def __str__(self):
        return f'Question №{self.pk}'
