from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Action


@login_required
def dashboard(request):
    """Отображает страницу с действиями пользователя."""
    
    if request.user.is_staff:
        action_list = Action.objects.select_related('user').prefetch_related('target')
    else:
        action_list = Action.objects.filter(user=request.user).prefetch_related('target')
        
    paginator = Paginator(action_list, 5)
    page = request.GET.get('page')
    action_only = request.GET.get('posts_only')

    try:
        actions = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        if action_only:
            return HttpResponse('')
        actions = paginator.page(1)
    
    if action_only:
        return render(request,
                      'actions/action/detail.html',
                      {'actions': actions})
    
    return render(request,
                  'actions/user_actions.html',
                  {'actions': actions})
