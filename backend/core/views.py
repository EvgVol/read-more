from django.views.generic import TemplateView
from django.shortcuts import render


class SettingView(TemplateView):
    """Отображает страницу со списком настроек."""
    template_name = 'core/settings.html'


class StyleView(TemplateView):
    """Отображает страницу с настройками стилей."""
    template_name = 'core/style.html'


class IndexView(TemplateView):
    """Отображает главную страницу"""
    template_name = 'core/landing-page.html'


def countdown_view(request):
    return render(request, 'core/countdown.html')