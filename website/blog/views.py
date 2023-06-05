import time

from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q
from django.contrib.postgres.search import (SearchVector, SearchQuery,
                                            SearchRank, TrigramSimilarity)
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from taggit.models import Tag

from actions.utils import create_action
from .models import Post, Category
from .forms import EmailPostForm, CommentForm, SearchForm, PostForm


def post_list(request, tag_slug=None, category_slug=None):
    """Отображает список статей."""
    # Отображаем только опубликованные статьи(черновики не показываем)
    post_list = Post.published.select_related('author', 'category')
    tag = None
    category = None

    # Отображение статей с выбранным тегом
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

    # Отображение статей с выбранной категорией
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        post_list = post_list.filter(category__in=[category])

    # Получаем 4 последние опубликованные статьи
    latest_posts = post_list.order_by('-publish')[:4]

    # Получаем список всех тегов, связанных со статьями
    tag_list = Tag.objects.annotate(total_posts=Count('post'))
    
    # Разбивка списка статей на страницы
    paginator = Paginator(post_list, 1) # Показывать 1 статью на странице
    page = request.GET.get('page')
    posts_only = request.GET.get('posts_only')

    # Отображаем запрошенную страницу
    try:
        posts = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        # Если страница не является целым числом или недействительна, отображаем первую страницу
        # Если параметр posts_only установлен в запросе, возвращаем только пустой ответ HTTP
        if posts_only:
            return HttpResponse('')
        posts = paginator.page(1)
    
    if posts_only:
        return render(request,
                      'blog/post/cart.html',
                      {'posts': posts})

    return render(request, 'blog/blog.html', {'posts': posts,
                                              'tag': tag,
                                              'latest_posts': latest_posts,
                                              'tag_list': tag_list,
                                              'category': 'category'})


# Отображаем детали статьи
def post_detail(request, year, month, day, post):
    """Отображает данные статьи."""

    # Получение статьи по заданным параметрам
    post =  get_object_or_404(Post,
                              status=Post.Status.PUBLISHED,
                              slug=post,
                              publish__year=year,
                              publish__month=month,
                              publish__day=day)
    # Получение списка активных комментариев для этой статьи
    comments = post.comments.filter(active=True)
     # Если пользователь оставил комментарий
    form = CommentForm()
    # Получение списка похожих статей
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids
    ).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags','-publish')[:4]
    # Получение списка всех тегов и количества статей, связанных с каждым тегом
    tag_list = Tag.objects.annotate(total_posts=Count('post'))
    
    return render(request, 'blog/blog-detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts,
                   'tag_list': tag_list})


# Поделиться статьей
def post_share(request, post_id):
    """Позволяет поделиться конкретной статьей."""
    post = get_object_or_404(Post,
                             id=post_id,
                             status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = f"{cd['name']} рекомендует вам прочитать статью \"{post.title}\""
            message = f"Прочитайте статью \"{post.title}\" здесь: {post_url}\n\n" \
                      f"Комментарий от {cd['name']}: {cd['comments']}"
            send_mail(subject, message, 'volochek93@yandex.ru', [cd['to']])
            create_action(request.user, 'поделился статьей')
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post,
                                                    'form': form,
                                                    'sent': sent})


# Оставляем комментарий к статье
@require_POST
def post_comment(request, post_id):
    """Оставляем комментарии к статье."""
    post = get_object_or_404(Post,
                             id= post_id,
                             status= Post.Status.PUBLISHED)
    form = CommentForm(data=request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
        create_action(request.user, 'прокомментировал')
    return render(request, 'blog/post/comment.html',
                  {'post': post,
                   'form': form,
                   'comment': comment})


def post_search(request):
    """Осуществляет поисковой запрос."""
    form = SearchForm()
    query = None
    results = []
    elapsed_time = 0

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + \
                            SearchVector('body', weight='B')
            search_query = SearchQuery(query, config='russian')
            # Засекаем время поиска
            start_time = time.time()
            # Осуществляем поиск 
            results = Post.published.annotate(
                search=search_vector,
                rank=SearchRank(search_vector, search_query),
                similarity=TrigramSimilarity('title', query) + \
                           TrigramSimilarity('body', query)
            ).filter(
                Q(search=search_query) | Q(search__icontains=query)
            ).filter(similarity__gt=0.1).order_by('-rank', '-similarity')
            # Оставливаем счетчик времени
            elapsed_time = time.time() - start_time
    # Возвращаем результаты поиска в шаблон
    return render(request, 'blog/post/search.html',
                    {'form': form,
                    'query': query,
                    'results': results,
                    'elapsed_time': elapsed_time})


@login_required
def create_post(request):
    """Осуществляет добавление новой статьи."""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            create_action(request.user, 'добавил статью')
            messages.success(request, 'Статья успешно добавлена')
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    return render(request, 'blog/post/create.html', {'form': form})


@csrf_exempt
@login_required
@require_POST
def post_like(request):
    """Осуществляет проставление отметки `Нравится` """
    post_id = request.POST.get('id')
    action = request.POST.get('action')
    if post_id and action:
        try:
            post = Post.objects.get(id=post_id)
            if action == 'like':
                post.users_like.add(request.user)
                create_action(request.user, 'оценил', post)
            else:
                post.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Post.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})
