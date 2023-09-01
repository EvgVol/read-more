from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.shortcuts import redirect

from courses.models.course import Course



class OwnerEditMixin:
    """
    A mixin that sets the requesting user as the owner of the object 
    being created or updated.
    """
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(PermissionRequiredMixin):
    """A mixin for views that deal with Course instances."""

    model = Course
    fields = ('subject', 'title', 'overview', 'description',
              'complexity', 'advantages', 'technologies', 'load',
              'period', 'count_projects', 'price_per_mouth',
              'price_immediately')

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