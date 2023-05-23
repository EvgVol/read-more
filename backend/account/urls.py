from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('account/', include([
        path('register/', views.register, name='signup'),
        path('', include('django.contrib.auth.urls')),
    ])),

    path('profile/', include([
        path('<int:pk>/', views.ProfileView.as_view(), name='profile'),
        path('edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    ]))
]
