import time

from django.shortcuts import get_object_or_404, render
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q
from django.views.generic import TemplateView
from django.contrib.postgres.search import (SearchVector, SearchQuery,
                                            SearchRank, TrigramSimilarity)


from taggit.models import Tag

from .models import Post, Category
from .forms import EmailPostForm, CommentForm, SearchForm


class SettingView(TemplateView):
    """Отображает страницу с настройками сайта."""

    template_name = 'blog/setting.html'


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

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        post_list = post_list.filter(category__in=[category])

    # Сортировка статей по дате публикации и вывод последних 4 статей
    latest_posts = post_list.order_by('-publish')[:4]

    # Получение списка всех тегов и количества статей, связанных с каждым тегом
    tag_list = Tag.objects.annotate(total_posts=Count('post'))

    # Пагинация статей
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 
                  'blog/blog.html',
                  {'posts': posts,
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
