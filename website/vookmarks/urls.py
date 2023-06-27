from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views


app_name = 'vookmarks'


urlpatterns = [
    path(_('create/'), views.image_create, name='create'),
    path('', views.image_list, name='list'),
    path(_('detail/<int:id>/<slug:slug>/'), views.image_detail, name='detail'),
    path(_('like/'), views.image_like, name='like'),
]
