from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from .views import (ManageCourseListView, CourseCreateView,
                    CourseUpdateView, CourseDeleteView,
                    CourseModuleUpdateView, ContentCreateUpdateView,
                    ContentDeleteView, ModuleContentListView,
                    SubjectView)


app_name = 'courses'


urlpatterns = [
    # Курс
    path("", SubjectView.as_view(), name="subject_list"),
    path("mine/", ManageCourseListView.as_view(), name="manage_course_list"),
    path("create/", CourseCreateView.as_view(), name="course_create"),
    path("<pk>/", include([
        path("edit/", CourseUpdateView.as_view(), name="course_edit"),
        path("delete/", CourseDeleteView.as_view(), name="course_delete"),

        # Модуль
        path('module/', include([
            path('', CourseModuleUpdateView.as_view(), name="module_update"),

            # Контент
            path('<int:module_id>/', include([
                # path('', ModuleContentListView.as_view(), name='content_list'),
                
                path('content/<str:model_name>/<int:id>/', include([
                    # path('', ContentCreateUpdateView.as_view(), name='content_update'),
                    path('delete/', ContentDeleteView.as_view(), name='content_delete'),
                ])),
            ])),
        ])),
    ])),
    path('<pk>/module/', CourseModuleUpdateView.as_view(), name='module_update'),
    path('module/<int:module_id>/content/<model_name>/create/', ContentCreateUpdateView.as_view(),name='content_create'),
    path('module/<int:module_id>/content/<model_name>/<id>/', ContentCreateUpdateView.as_view(), name='content_update'),
    path('content/<int:module_id>/', ModuleContentListView.as_view(), name='content_list'),
    path('module/<int:module_id>/content/<str:model_name>/create/', ContentCreateUpdateView.as_view(), name='content_create'),
]
