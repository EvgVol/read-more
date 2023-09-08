from django.contrib.auth import login, get_user_model, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from actions.utils import create_action
from .forms import RegisterForm, UserEditForm, PasswordChangingForm
from .models import Profile, Contact
from actions.models import Action

User = get_user_model()


def register(request):
    """Регистрирует новых пользователей."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            new_user.backend = 'django.contrib.auth.backends.ModelBacken'
            login(request, new_user)
            Profile.objects.create(user=new_user)
            create_action(new_user, 'зарегистрировался', new_user)
        return redirect('blog:post_list')
    else:
        form = RegisterForm()
    return render(request,
                  'registration/signup.html',
                  {'form': form})

@login_required
def user_detail(request, username):
    """Отображает данные пользователя."""
    author = get_object_or_404(User, username=username, is_active=True)
    post_list = author.blog_posts.all()
    followers = author.followers.order_by('-username').all()
    courses = author.courses_joined.all()
    actions = Action.objects.select_related('user')[:6]
    context = {
        'author': author,
        'post_list': post_list,
        'followers': followers,
        'courses': courses,
        'actions': actions,
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
                create_action(user, 'изменил свои данные', user)
                messages.success(request, 'Данные профиля изменены')
        elif 'change-password' in request.POST:
            if form_password.is_valid():
                form_password.save()
                logout(request)
                create_action(user, 'изменил свои данные', user)
                messages.success(request, 'Пароль успешно изменен')
                return redirect('login')
    return render(request, 'account/profile-edit.html',
                  {'form': form,
                   'form_password': form_password})


@user_passes_test(lambda user: user.is_staff)
@login_required
def user_list(request):
    users = User.objects.all()
    return render(request,
                  'account/user-list.html',
                  {'section': 'people',
                   'users': users})


@csrf_exempt
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id=user_id)
            if action == 'follow':
                Contact.objects.get_or_create(
                    user_from=request.user,
                    user_to=user
                )
                create_action(request.user, 'подписался на', user)
            else:
                Contact.objects.filter(
                    user_from=request.user, user_to=user
                ).delete()
                create_action(request.user, 'отписался от', user)
            return JsonResponse({'status':'ok'})
        except User.DoesNotExist:
            return JsonResponse({'status':'error'})
    return JsonResponse({'status':'error'})
