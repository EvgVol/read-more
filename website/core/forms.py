from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Question


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('first_name', 'email', 'content',)
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'aria-describedby': 'first_name-help'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'aria-describedby': 'email-help'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'aria-describedby': 'content-help'}),
        }
        error_messages = {
            'first_name': {
                'required': _('Please, enter your name'),
            },
            'email': {
                'required': _('Please, enter your email adress'),
            },
            'content': {
                'required': _('Please leave your question'),
            }
        }
        help_texts = {
            'first_name': _('Пожалуйста укажите своё имя'),
            'email': _('Пожалуйста укажите свою электронную почту'),
            'content': _('Укажите ваш вопрос'),
        }
