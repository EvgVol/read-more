from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from courses.views.generic.list import (CourseListView, SubjectView,
                                        ContentListView, ModuleListView)
from courses.views.generic.detail import CourseDetailView
from courses.views.generic.create import (CourseCreateView,
                                          ContentCreateUpdateView,)
from courses.views.generic.update import CourseUpdateView, ModuleUpdateView
from courses.views.generic.delete import CourseDeleteView, ContentDeleteView

app_name = 'courses'


urlpatterns = [
    path("",
         SubjectView.as_view(), name="subject_list"),
    path("create/", 
         CourseCreateView.as_view(), name="course_create"),
    path("courses/<subject_name>/",
         CourseListView.as_view(), name="manage_course_list"),
    path("course/<int:pk>/", include([
        path("", CourseDetailView.as_view(), name="course_detail"),
        path('modules/', ModuleListView.as_view(), name='module_list'),
    ])),
    path("courses/<int:pk>/", include([
        path("edit/",
             CourseUpdateView.as_view(), name="course_edit"),
        path("delete/",
             CourseDeleteView.as_view(), name="course_delete"),
        path('module/', include([
            path('', ModuleUpdateView.as_view(), name="module_update"),
            # path('<int:module_id>', ContentListView.as_view(), name="content_list"),
        ])),
    ])),
    path('module/<int:module_id>/', ContentListView.as_view(), name="content_list"),
    path('module/<int:module_id>/content/<model_name>/create/', ContentCreateUpdateView.as_view(), name='content_create'),
    path('module/<int:module_id>/content/<model_name>/<int:id>/', ContentCreateUpdateView.as_view(), name='content_update'),
    path('content/<int:id>/delete/', ContentDeleteView.as_view(), name='content_delete'),
]
