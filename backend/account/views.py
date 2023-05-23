from django.contrib.auth import login, get_user_model
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib.auth.views import (PasswordChangeDoneView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import reverse_lazy
from django.db import transaction


from .forms import RegisterForm, ProfileUpdateForm

User = get_user_model()


# class PasswordChangeDone(PasswordChangeDoneView):
#     template_name = 'account/password_change_done.html'


# class PasswordChange(PasswordChangeView):
#     success_url = reverse_lazy('account:password_change_done')
#     template_name = 'account/password_change_form.html'


# class PasswordResetComplete(PasswordResetCompleteView):
#     template_name = 'account/password_reset_complete.html'


# class PasswordResetConfirm(PasswordResetConfirmView):
#     success_url = reverse_lazy('account:password_reset_complete')
#     template_name = 'account/password_reset_confirm.html'


# class PasswordResetDone(PasswordResetDoneView):
#     template_name = 'account/password_reset_done.html'


# class PasswordReset(PasswordResetView):
#     success_url = reverse_lazy('account:password_reset_done')
#     template_name = 'account/password_reset_form.html'


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
    form_class = ProfileUpdateForm
    template_name = 'account/profile-edit.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактирование профиля пользователя: {self.request.user.username}'
        form = kwargs.get('form')
        if not form:
            form = self.form_class(instance=self.request.user)
        context['user_form'] = form
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        user_form = context['user_form']
        with transaction.atomic():
            if all([form.is_valid(), user_form.is_valid()]):
                user_form.save()
                form.save()
            else:
                context.update({'user_form': user_form})
                return self.render_to_response(context)
        return super(ProfileUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse_lazy('account:profile', kwargs={'pk': self.object.pk})