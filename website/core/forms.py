from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Question


class QuestionForm(forms.ModelForm):

    class Meta:
        model = Question
        fields = ('first_name', 'email', 'content',)
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
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
