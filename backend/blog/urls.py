from django.urls import path, include

from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/',
         views.post_detail,
         name='post_detail'),
    path('<int:post_id>/', include([
        path('share/', views.post_share, name='post_share'),
        path('comment/', views.post_comment, name='post_comment'),
    ])),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('category/<slug:category_slug>/', views.post_list, name='post_list_by_category'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
    path('search/', views.post_search, name='post_search'),
    path('setting/', views.SettingView.as_view(), name='setting'),
]
