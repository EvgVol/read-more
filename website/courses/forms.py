from django import forms
from django.forms.models import inlineformset_factory

from courses.models import course, module


ModuleFormSet = inlineformset_factory(course.Course,
                                      module.Module,
                                      fields=['title', 'description'],
                                      extra=2,
                                      can_delete=True)
