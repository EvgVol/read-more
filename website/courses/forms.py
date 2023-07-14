from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from courses.models.advantage import Advantage
from courses.models.technology import Technology
from courses.models.course import Course, Card


class CourseForm(forms.ModelForm):
    advantages = forms.ModelMultipleChoiceField(
        queryset=Advantage.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Advantages', is_stacked=False)
    )
    technologies = forms.ModelMultipleChoiceField(
        queryset=Technology.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Technologies', is_stacked=False)
    )
    cards = forms.ModelMultipleChoiceField(
        queryset=Card.objects.all(),
        widget=FilteredSelectMultiple(verbose_name='Cards', is_stacked=False)
    )

    class Meta:
        model = Course
        fields = '__all__'
