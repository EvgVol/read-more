from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from . import views


urlpatterns = [
    path(_('account/'), include([
        path(_('register/'), views.register, name='signup'),
        path('', include('django.contrib.auth.urls')),
        path(_('edit/'), views.user_edit, name='account_edit'),
    ])),

    path(_('profile/'), include([
        path('<str:username>/', views.user_detail, name='profile'),
        
    ])),

    path(_('users/'), views.user_list, name='user_list'),
    path(_('users/follow/'), views.user_follow, name='user_follow'),
]
