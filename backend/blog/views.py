from django.shortcuts import render, get_object_or_404
from django.views import generic

from .models import Post


# class BlogListView(generic.ListView):
#     """Отображает страницу блога с 8 постами."""

#     model = Post
#     template_name = "blog/blog.html"
#     paginate_by = 4



def post_list(request):
    posts = Post.published.all()
    return render(request, 'blog/blog.html', {'posts': posts})


def post_detail(request):
    post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISH)
    return render(request, 'blog/post/post_detail.html', {'post': post})
