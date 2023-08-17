from django.forms.models import inlineformset_factory

from courses.models.course import Course
from courses.models.module import Module


ModuleFormSet = inlineformset_factory(Course, Module,
                                      fields=['title', 'description'],
                                      extra=1,
                                      can_delete=True)
