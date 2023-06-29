from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from .views import (ManageCourseListView, CourseCreateView,
                    CourseUpdateView, CourseDeleteView)


app_name = 'courses'


urlpatterns = [
    path("mine/", ManageCourseListView.as_view(), name="manage_course_list"),
    path("create/", CourseCreateView.as_view(), name="course_create"),
    path("<pk>/", include([
        path("edit/", CourseUpdateView.as_view(), name="course_edit"),
        path("delete/", CourseDeleteView.as_view(), name="course_delete")
    ])),
]
