from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model 

from blog.models import Post, Comment

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
        """Перенаправляет авторизованного пользователя на главную страницу"""
        if request.user.is_authenticated:
            return redirect('core:home')
        else:
            return super().dispatch(request, *args, **kwargs)


class HomePageView(TemplateView):
    """Отображает главную страницу."""

    template_name = 'core/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        """Перенаправляет неавторизованного пользователя на лендинг"""
        if request.user.is_anonymous:
            return redirect('core:index')
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_count'] = get_user_model().objects.count()
        context['post_count'] = Post.objects.count()
        context['comment_count'] = Comment.objects.count()
        context['like_count'] = sum(post.users_like.count() for post in Post.objects.all())
        return context

def countdown_view(request):
    return render(request, 'core/countdown.html')