from django.views.generic import ListView, DetailView

from .models import Post


class PostListView(ListView):
    """Представление списка постов."""

    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/blog.html'


class PostDetailView(DetailView):
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
