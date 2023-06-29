from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .models import Course


class OwnerMixin:
    """
    A mixin that limits queryset to those created by the requesting user. 
    Used in conjunction with Django's built-in authentication system.
    """
    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class OwnerEditMixin:
    """
    A mixin that sets the requesting user as the owner of the object 
    being created or updated. Used in conjunction with Django's built-in 
    authentication system.
    """
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin,
                       LoginRequiredMixin,
                       PermissionRequiredMixin):
    """
    A mixin for views that deal with Course instances. 
    Limits queryset to courses created by the requesting user,
    requires users to be logged in, and enforces the `view_course` permission.
    """
    model = Course
    fields = ['subjects', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    """
    A mixin for views that edit Course instances. 
    Limits queryset to courses created by the requesting user,
    requires users to be logged in, and enforces the `add_course` 
    or `change_course` permission.
    
    Sets the owner of the instance being created or updated 
    to the requesting user.
    """
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    """
    A view for displaying a list of courses. 
    Limits queryset to courses created by the requesting user,
    requires users to be logged in, and enforces the `view_course` permission.
    """
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    """
    A view for creating a new course. 
    Limits queryset to courses created by the requesting user, requires 
    users to be logged in, and enforces the `add_course` permission. 
    Sets the owner of the course to the requesting user upon creation.
    """
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    """
    A view for updating an existing course. 
    Limits queryset to courses created by the requesting user, requires 
    users to be logged in, and enforces the `change_course` permission. 
    Sets the owner of the course being updated to the requesting user.
    """
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    """
    A view for deleting an existing course. 
    Limits queryset to courses created by the requesting user, requires 
    users to be logged in, and enforces the `delete_course` permission.
    """
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'
