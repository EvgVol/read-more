from django.contrib.auth import login, get_user_model
from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.db import transaction
from django.shortcuts import render, redirect

from .forms import RegisterForm, ProfileUpdateForm


User = get_user_model()


def register(request):
    """Регистрирует новых пользователей."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
        return redirect('blog:post_list')
    else:
        form = RegisterForm()
    return render(request,
                  'registration/signup.html',
                  {'form': form})



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