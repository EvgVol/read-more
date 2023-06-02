from django.urls import path, include

from . import views

app_name = 'core'


urlpatterns = [
    path('', views.LangingPageView.as_view(), name='index'),
    path('home/', views.HomePageView.as_view(), name='home'),
    path('setting/', views.SettingView.as_view(), name='setting'),
    path('style/', views.StyleView.as_view(), name='style'),
    path('countdown/', views.countdown_view, name='countdown_view'),
    
]
