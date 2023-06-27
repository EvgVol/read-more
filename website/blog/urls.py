from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from . import views
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path(_('add/'), views.create_post, name='post_create'),
    path(_('like/'), views.post_like, name='post_like'),
    path(_('<int:year>/<int:month>/<int:day>/<slug:post>/'),
         views.post_detail,
         name='post_detail'),
    path('<int:post_id>/', include([
        path(_('share/'), views.post_share, name='post_share'),
        path(_('comment/'), views.post_comment, name='post_comment'),
    ])),
    path(_('tag/<slug:tag_slug>/'), views.post_list, name='post_list_by_tag'),
    path(_('category/<slug:category_slug>/'), views.post_list, name='post_list_by_category'),
    path(_('feed/'), LatestPostsFeed(), name='post_feed'),
    path(_('search/'), views.post_search, name='post_search'),
    path(_('ranking/<slug:ranking>'), views.post_list, name='post_list_ranking'),
]
