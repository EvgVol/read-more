from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from courses.models.advantage import Advantage
from courses.models.technology import Technology
from courses.models.course import Course


class CourseForm(forms.ModelForm):
    advantages = forms.ModelMultipleChoiceField(
        queryset=Advantage.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Advantages', is_stacked=False)
    )
    technologies = forms.ModelMultipleChoiceField(
        queryset=Technology.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Technologies', is_stacked=False)
    )

    class Meta:
        model = Course
        fields = '__all__'


class CourseEnrollForm(forms.Form):
    course = forms.ModelChoiceField(queryset=Course.objects.all(),
                                    widget=forms.HiddenInput)
