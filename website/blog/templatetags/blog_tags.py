from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

from ..models import Post, Category


register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.simple_tag
def get_most_commented_posts(count=3):
    return Post.published.annotate(
        total_comments=Count('comments')
    ).filter(total_comments__gt=1).order_by('-total_comments')[:count]


@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text))


@register.inclusion_tag('blog/includes/categories.html')
def show_categories():
    categories = Category.objects.annotate(
        num_posts=Count('posts')
    ).filter(num_posts__gt=0)\
     .order_by('-num_posts')
    return {'categories': categories}
