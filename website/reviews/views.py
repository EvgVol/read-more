# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.auth.decorators import login_required

# from .models import Review
# from .forms import ReviewForm

# @login_required
# def create_review(request, content_type_id, object_id):
#     content_type = get_object_or_404(ContentType, id=content_type_id)
#     content_object = content_type.get_object_for_this_type(pk=object_id)

#     if request.method == "POST":
#         form = ReviewForm(request.POST)
#         if form.is_valid():
#             new_review = form.save(commit=False)
#             new_review.content_object = content_object
#             new_review.author = request.user
#             new_review.save()
#             return redirect(request.META.get('HTTP_REFERER'))
#     else:
#         form = ReviewForm()
#     return render(request, 'comment_form.html', {'form': form, 'content_type_id': content_type_id, 'object_id': object_id})