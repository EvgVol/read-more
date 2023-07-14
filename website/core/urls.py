from django.urls import path, include
from django.utils.translation import gettext_lazy as _

from . import views


app_name = 'core'


urlpatterns = [
    path('', views.LangingPageView.as_view(), name='index'),
    path(_('home/'), views.HomePageView.as_view(), name='home'),
    path(_('setting/'), views.SettingView.as_view(), name='setting'),
    path(_('style/'), views.StyleView.as_view(), name='style'),
    path(_('countdown/'), views.countdown_view, name='countdown_view'),
    path(_('test/'), views.TestPageView.as_view(), name='test_page'),
]
