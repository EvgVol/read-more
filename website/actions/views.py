from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from .models import Action


@login_required
def dashboard(request):
    """Отображает страницу с действиями пользователя."""
    
    if request.user.is_staff:
        action_list = Action.objects.all()
    else:
        action_list = Action.objects.filter(user=request.user)
        
    paginator = Paginator(action_list, 10) # Показывать 10 действий на странице
    page = request.GET.get('page')

    try:
        actions = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        actions = paginator.page(1)
    
    actions_only = request.GET.get('actions_only')
    
    if actions_only:
        return render(request, 'actions/action/detail.html', {'actions': actions})
    
    return render(request, 'actions/user_actions.html', {'actions': actions})
