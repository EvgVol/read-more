from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model 

from blog.models import Post, Comment
from actions.models import Action
from courses.models.course import Course


class SettingView(TemplateView):
    """Отображает страницу со списком настроек."""

    template_name = 'core/settings.html'


class StyleView(TemplateView):
    """Отображает страницу с настройками стилей."""

    template_name = 'core/style.html'


# class LangingPageView(TemplateView):
#     """Отображает страницу лендинг."""

#     template_name = 'core/landing-page.html'

#     def dispatch(self, request, *args, **kwargs):
#         """Перенаправляет авторизованного пользователя на главную страницу"""
#         if request.user.is_authenticated:
#             return redirect('core:dashboard')
#         else:
#             return super().dispatch(request, *args, **kwargs)


class DashboardPageView(TemplateView):
    """Отображает главную страницу."""

    template_name = 'core/dashboard.html'

    # def dispatch(self, request, *args, **kwargs):
    #     """Перенаправляет неавторизованного пользователя на лендинг"""
    #     if request.user.is_anonymous:
    #         return redirect('core:index')
    #     else:
    #         return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_courses = Course.objects.all()
        junior_courses = Course.objects.filter(complexity=Course.Complexity.JUNIOR)
        middle_courses = Course.objects.filter(complexity=Course.Complexity.MIDDLE)
        senior_courses = Course.objects.filter(complexity=Course.Complexity.SENIOR)

        total_count = all_courses.count()
        junior_count = junior_courses.count()
        middle_count = middle_courses.count()
        senior_count = senior_courses.count()

        # Calculate percentages
        if total_count > 0:
            percent_junior = (junior_count / total_count) * 100
            percent_middle = (middle_count / total_count) * 100
            percent_senior = (senior_count / total_count) * 100
        else:
            percent_junior = 0
            percent_middle = 0
            percent_senior = 0

        context['all_courses'] = all_courses
        context['junior_courses'] = junior_courses
        context['middle_courses'] = middle_courses
        context['senior_courses'] = senior_courses
        context['percent_junior'] = percent_junior
        context['percent_middle'] = percent_middle
        context['percent_senior'] = percent_senior
        context['user_count'] = get_user_model().objects.count()
        context['post_count'] = Post.objects.count()
        context['comment_count'] = Comment.objects.count()
        context['actions'] = Action.objects.select_related('user')[:6]
        context['like_count'] = sum(post.users_like.count() for post in Post.objects.all())
        return context

def countdown_view(request):
    return render(request, 'core/countdown.html')


class TestPageView(TemplateView):
    template_name = 'courses/manage/module/module_list.html'