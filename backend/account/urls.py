from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('account/', include([
        path('register/', views.register, name='signup'),
        path('', include('django.contrib.auth.urls')),
        path('edit/', views.user_edit, name='account_edit'),
    ])),

    path('profile/', include([
        path('<str:username>/', views.user_detail, name='profile'),
    ]))
]
