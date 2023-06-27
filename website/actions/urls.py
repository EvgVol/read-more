from django.urls import path
from django.utils.translation import gettext_lazy as _

from . import views


app_name = 'actions'


urlpatterns = [
    path(_('notification/'), views.dashboard, name='notification'),
]

