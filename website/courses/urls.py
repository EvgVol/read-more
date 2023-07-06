from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from .views import (ManageCourseListView, CourseCreateView,
                    CourseUpdateView, CourseDeleteView,
                    CourseModuleUpdateView, ContentCreateUpdateView,
                    ContentDeleteView, ModuleContentListView)


app_name = 'courses'


urlpatterns = [
    # Курс
    path("mine/", ManageCourseListView.as_view(), name="manage_course_list"),
    path("create/", CourseCreateView.as_view(), name="course_create"),
    path("<int:pk>/", include([
        path("edit/", CourseUpdateView.as_view(), name="course_edit"),
        path("delete/", CourseDeleteView.as_view(), name="course_delete"),

        # Модуль
        path('module/', include([
            path('', CourseModuleUpdateView.as_view(),name="module_update"),

            # Контент
            path('<int:module_id>/', include([
                path('',
                    ModuleContentListView.as_view(),
                    name='content_list'),
                path('content/<model_name>/', include([
                    path('create/',
                        ContentCreateUpdateView.as_view(),
                        name="content_create"),
                    path('<int:id>/', include([
                        path('',
                            ContentCreateUpdateView.as_view(),
                            name='content_update'),
                        path('delete/',
                            ContentDeleteView.as_view(),
                            name='content_delete'),
                    ])),
                ])),
            ])),
        ])),
    ])),
]
