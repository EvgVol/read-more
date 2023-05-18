from django.shortcuts import get_object_or_404, render
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count

from taggit.models import Tag

from .models import Post
from .forms import EmailPostForm, CommentForm



def post_list(request, tag_slug=None):
    """Отображает список статей."""
    # Отображаем только опубликованные статьи(черновики не показываем)
    post_list = Post.published.all()
    tag = None

    # Отображение статей с выбранным тегом
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])

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
                   'tag_list': tag_list})


# Отображаем детали статьи
def post_detail(request, year, month, day, post):
    """Отображает детали статьи."""
    
    post =  get_object_or_404(Post,
                              status=Post.Status.PUBLISHED,
                              slug=post,
                              publish__year=year,
                              publish__month=month,
                              publish__day=day)
    comments = post.comments.filter(active=True)
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
    
    # # Получение списка похожих авторов
    # similar_authors_list = get_similar_authors(post, count=4)
    
    return render(request, 'blog/blog-detail.html',
                  {'post': post,
                   'comments': comments,
                   'form': form,
                   'similar_posts': similar_posts,
                   'tag_list': tag_list})
                #    'similar_authors_list': similar_authors_list})


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


# def get_similar_authors(post, count=4):
#     """Возвращает список авторов похожих постов."""
#     post_tags_ids = post.tags.values_list('id', flat=True)
#     similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
#     similar_authors = []
#     for p in similar_posts:
#         if p.author not in similar_authors:
#             similar_authors.append(p.author)
#     current_author = post.author
#     similar_authors = list(filter(lambda a: a != current_author, similar_authors))
#     return similar_authors[:count]