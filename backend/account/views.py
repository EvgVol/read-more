from django.contrib.auth import login, get_user_model
from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy

from .forms import RegisterForm

User = get_user_model()


class RegisterView(CreateView):
    """Отображение страницы регистрации."""
    form_class = RegisterForm
    success_url = reverse_lazy('blog:post_list')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        valid = super().form_valid(form)
        login(self.request, self.object)
        return valid


class ProfileView(DetailView):
    """Отображение страницы пользователя."""

    model = User
    template_name = 'account/profile.html'


class ProfileUpdateView(UpdateView):
    """Отображение страницы редактирования профиля пользователя."""

    model = User
    # form_class = UserUpdateForm
    template_name = 'account/profile-edit.html'