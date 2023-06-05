from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Action


@login_required
def dashboard(request):
    if request.user.is_superuser:
        actions = Action.objects.all()
    else:
        actions = Action.objects.filter(user=request.user)
    return render(request,
                  'actions/user_actions.html',
                  {'actions': actions})
