from django.urls import path, include

from . import views


urlpatterns = [
    path('account/', include([
        path('register/', views.register, name='signup'),
        path('', include('django.contrib.auth.urls')),
        path('edit/', views.user_edit, name='account_edit'),
    ])),

    path('profile/', include([
        path('<str:username>/', views.user_detail, name='profile'),
        
    ])),

    path('users/', views.user_list, name='user_list'),
    path('users/follow/', views.user_follow, name='user_follow'),
]
