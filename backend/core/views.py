from django.views.generic import TemplateView
from django.shortcuts import render, redirect


class SettingView(TemplateView):
    """Отображает страницу со списком настроек."""

    template_name = 'core/settings.html'


class StyleView(TemplateView):
    """Отображает страницу с настройками стилей."""

    template_name = 'core/style.html'


class LangingPageView(TemplateView):
    """Отображает страницу лендинг."""

    template_name = 'core/landing-page.html'

    def dispatch(self, request, *args, **kwargs):
        """Перенаправляет авторизованного пользователя на страницу блога"""
        if request.user.is_authenticated:
            return redirect('blog:post_list')
        else:
            return super().dispatch(request, *args, **kwargs)


def countdown_view(request):
    return render(request, 'core/countdown.html')