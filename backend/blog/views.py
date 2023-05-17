from django.views.generic import ListView, DetailView, FormView
from django.shortcuts import get_object_or_404, render
from django.core.mail import send_mail

from .models import Post
from .forms import EmailPostForm


class PostListView(ListView):
    """Представление списка постов."""

    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/blog.html'


class PostDetailView(DetailView):
    """Представление поста."""

    model = Post
    context_object_name = 'post'
    template_name = 'blog/blog-detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            status=Post.Status.PUBLISHED,
            publish__year=self.kwargs['year'],
            publish__month=self.kwargs['month'],
            publish__day=self.kwargs['day'],
            slug=self.kwargs['post']
        )


def post_share(request, post_id):
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