from django.urls import path, include

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', include([
        path('', views.PostDetailView.as_view(), name='post_detail'),
        # path('share/', views.post_share, name='post_share'),
    ])),
]
