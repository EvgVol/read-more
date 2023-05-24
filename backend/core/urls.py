from django.urls import path, include

from . import views

app_name = 'core'


urlpatterns = [
    path('settings/', views.SettingView.as_view(), name='setting'),
    path('style/', views.StyleView.as_view(), name='style'),
]
