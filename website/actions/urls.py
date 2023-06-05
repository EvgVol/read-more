from django.urls import path

from . import views


app_name = 'actions'


urlpatterns = [
    path('notification/', views.dashboard, name='notification'),
]

