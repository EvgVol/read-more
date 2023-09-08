from django.shortcuts import redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from actions.utils import create_action
from .forms import ReviewForm


@require_POST
@login_required
def create_review(request, content_type_id, object_id):
    content_type = get_object_or_404(ContentType, id=content_type_id)
    content_object = content_type.get_object_for_this_type(pk=object_id)
    author = request.user
    
    form = ReviewForm(request.POST)

    if form.is_valid():
        new_review = form.save(commit=False)
        new_review.content_object = content_object
        new_review.author = author
        new_review.save()
        messages.success(request, _('Your comment has been add'))
        create_action(author, _('commented:'), content_object)
    else:
        form = ReviewForm()
    return redirect(content_object.get_absolute_url())
