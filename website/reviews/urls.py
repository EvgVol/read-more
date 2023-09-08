from django.urls import path

from . views import create_review

app_name='reviews'


urlpatterns = [
    path('create-review/<int:content_type_id>/<int:object_id>/', create_review, name='create_review')
]
