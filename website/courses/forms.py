from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.forms.models import inlineformset_factory

from courses.models import subject, course, module, advantage, technology


ModuleFormSet = inlineformset_factory(course.Course,
                                      module.Module,
                                      fields=['title', 'description'],
                                      extra=2,
                                      can_delete=True)


class CourseForm(forms.ModelForm):
    advantages = forms.ModelMultipleChoiceField(
        queryset=advantage.Advantage.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Advantages', is_stacked=False)
    )
    technologies = forms.ModelMultipleChoiceField(
        queryset=technology.Technology.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Technologies', is_stacked=False)
    )
    cards = forms.ModelMultipleChoiceField(
        queryset=course.Card.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Cards', is_stacked=False)
    )

    class Meta:
        model = course.Course
        fields = '__all__'
