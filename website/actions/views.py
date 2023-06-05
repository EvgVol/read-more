from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Action


@login_required
def dashboard(request):
    actions = Action.objects.all()
    # following_ids = request.user.following.values_list('id', flat=True)
    # if following_ids:
    #     actions = actions.filter(user_id__in=following_ids)
    # actions = actions[:10]
    return render(request,
                  'actions/user_actions.html',
                  {'actions': actions})
