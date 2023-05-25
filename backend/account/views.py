from django.contrib.auth import login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .forms import RegisterForm, UserEditForm, PasswordChangingForm


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


def user_detail(request, username):
    """Отображает данные пользователя."""
    author = get_object_or_404(User, username=username)
    post_list = author.blog_posts.all()
    context = {
        'author': author,
        'post_list': post_list,
    }
    return render(request, 'account/profile.html', context)


@login_required
def user_edit(request):
    """Редактируем данные пользователя."""
    user = request.user
    form = UserEditForm(instance=user,
                        data=request.POST or None,
                        files=request.FILES or None)
    form_password = PasswordChangingForm(user=user,
                                         data=request.POST or None)
    if request.method == 'POST':
        if 'save-details' in request.POST:
            if form.is_valid():
                form.save()
        elif 'change-password' in request.POST:
            if form_password.is_valid():
                form_password.save()
                logout(request)
                return redirect('login')
    return render(request, 'account/profile-edit.html',
                  {'form': form,
                   'form_password': form_password})

#     author = get_object_or_404(User, username=username)
#     post_list = author.blog_posts.select_related('category').all()


# class ProfileView(DetailView):
#     """Отображение страницы пользователя."""

#     model = User
#     template_name = 'account/profile.html'


# class ProfileUpdateView(UpdateView):
#     """Отображение страницы редактирования профиля пользователя."""

#     model = User
#     form_class = ProfileUpdateForm
#     template_name = 'account/profile-edit.html'

#     def get_object(self, queryset=None):
#         return self.request.user

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['title'] = f'Редактирование профиля пользователя: {self.request.user.username}'
#         form = kwargs.get('form')
#         if not form:
#             form = self.form_class(instance=self.request.user)
#         context['user_form'] = form
#         return context

#     def form_valid(self, form):
#         context = self.get_context_data()
#         user_form = context['user_form']
#         with transaction.atomic():
#             if all([form.is_valid(), user_form.is_valid()]):
#                 user_form.save()
#                 form.save()
#             else:
#                 context.update({'user_form': user_form})
#                 return self.render_to_response(context)
#         return super(ProfileUpdateView, self).form_valid(form)

#     def get_success_url(self):
#         return reverse_lazy('account:profile', kwargs={'pk': self.object.pk})