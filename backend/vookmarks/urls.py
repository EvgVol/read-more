from django.urls import path

from . import views


app_name = 'vookmarks'


urlpatterns = [
    path('create/', views.image_create, name='create')
]
