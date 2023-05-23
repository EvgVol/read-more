from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    path('account/', include([
        path('register/', views.register, name='signup'),
        path('', include('django.contrib.auth.urls')),
    ])),
    # path('signup/', views.RegisterView.as_view(), name='signup'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    # path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    # path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    # path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # path('', include('django.contrib.auth.urls')),
    path('profile/', include([
        path('<int:pk>/', views.ProfileView.as_view(), name='profile'),
        path('edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    ]))
]
