from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import redis

from actions.utils import create_action
from .forms import ImageCreateForm
from .models import Image


r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)


@login_required
def image_create(request):
    if request.method == 'POST':
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'добавил закладку', new_image)
            messages.success(request, 'Изображение успешно добавлено')
            return redirect(new_image.get_absolute_url())
    else:
        form = ImageCreateForm(data=request.GET)

    return render(request,'vookmarks/image/create.html',
                  {'section': 'images', 'form': form})


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    total_views = r.incr(f'Изображение:{image.id}:просмотрено')
    return render(request, 'vookmarks/image/detail.html',
                  {'section': 'images',
                   'image': image,
                   'total_views': total_views})


@csrf_exempt
@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'лайкнул', image)
            else:
                image.users_like.remove(request.user)
                return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})


@login_required
def image_list(request):
    images = Image.objects.select_related('user')
    paginator = Paginator(images, 2)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        if images_only:
            return HttpResponse('')
        images = paginator.page(1)

    for image in images:
        total_views = r.get(f'Изображение:{image.id}:просмотрено')

        # преобразуйте total_views из bytes в int
        total_views = int(total_views) if total_views else 0
        image.total_views = total_views

    if images_only:
        return render(request,
                      'vookmarks/image/list_images.html',
                      {'images': images})

    return render(request,
                  'vookmarks/image/list.html',
                  {'images': images})