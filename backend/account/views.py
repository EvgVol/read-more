from django.contrib.auth import login, get_user_model
from django.views.generic import CreateView, DetailView, UpdateView


User = get_user_model()


class ProfileView(DetailView):
    """Отображение страницы пользователя."""

    model = User
    template_name = 'account/profile.html'
