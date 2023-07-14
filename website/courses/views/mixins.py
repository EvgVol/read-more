from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.urls import reverse
from django.shortcuts import redirect

from courses.models.course import Course


class OwnerMixin:
    """
    A mixin that limits queryset to those created by the requesting user.
    """
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class OwnerEditMixin:
    """
    A mixin that sets the requesting user as the owner of the object 
    being created or updated.
    """
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin,
                       LoginRequiredMixin,
                       PermissionRequiredMixin):
    """A mixin for views that deal with Course instances."""

    model = Course
    fields = ['subject', 'title', 'overview']

    def get_success_url(self):
        subject_name = self.object.subject.slug
        return reverse('courses:manage_course_list',
                       kwargs={'subject_name': subject_name})


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    """A mixin for views that edit Course instances."""

    template_name = 'courses/manage/course/form.html'

    def form_valid(self, form):
        super().form_valid(form)
        return redirect(self.get_success_url())