from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page

from courses.views.generic.list import (CourseListView, SubjectView,
                                        ContentListView, ModuleListView,
                                        ModuleOrderView, ContentOrderView)
from courses.views.generic.detail import CourseDetailView, CourseTrainerView
from courses.views.generic.create import (CourseCreateView,
                                          ContentCreateUpdateView,)
from courses.views.generic.update import CourseUpdateView, ModuleUpdateView
from courses.views.generic.delete import CourseDeleteView, ContentDeleteView
from courses.views.enrollment import StudentEnrollCourseView

app_name = 'courses'


urlpatterns = [
    path("",
         SubjectView.as_view(), name="subject_list"),
    path("create/", 
         CourseCreateView.as_view(), name="course_create"),
    path("course/<slug:slug>/trainer/",
         cache_page(60 * 15)(CourseTrainerView.as_view()), name="course_trainer"),
    path("course/<slug:slug>/trainer/<module_id>/",
         cache_page(60 * 15)(CourseTrainerView.as_view()), name="course_trainer_module"),
    path("courses/",
         CourseListView.as_view(), name="course_list"),
    path("courses/",
         CourseListView.as_view(), name="manage_course_list"),
    path("courses/<int:pk>/", include([
        path("edit/",
             CourseUpdateView.as_view(), name="course_edit"),
        path("delete/",
             CourseDeleteView.as_view(), name="course_delete"),
        path('module/', include([
            path('', ModuleUpdateView.as_view(), name="module_update"),
        ])),
    ])),
    path("course/<int:pk>/", include([
        path("", CourseDetailView.as_view(), name="course_detail"),
        path('modules/', ModuleListView.as_view(), name='module_list'),
    ])),
    
    path('module/<int:module_id>/', ContentListView.as_view(), name="content_list"),  
    path('module/<int:module_id>/content/<model_name>/create/', ContentCreateUpdateView.as_view(), name='content_create'),
    path('module/<int:module_id>/content/<model_name>/<int:id>/', ContentCreateUpdateView.as_view(), name='content_update'),
    path('content/<int:id>/delete/', ContentDeleteView.as_view(), name='content_delete'),
    path('module/order/', ModuleOrderView.as_view(), name='module_order'),
    path('content/order/', ContentOrderView.as_view(), name='content_order'),
    path('enroll-course/', StudentEnrollCourseView.as_view(), name='student_enroll_course'),
]
