from django.urls import path, include

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', include([
        path('', views.post_detail, name='post_detail'),
    ])),
]
