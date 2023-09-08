from django import template
from django.db import models
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType
import markdown

from ..models import Post, Category


register = template.Library()


@register.simple_tag
def total_posts():
    return Post.published.count()


@register.simple_tag
def get_most_commented_posts(count=3):
    post_content_type = ContentType.objects.get_for_model(Post)
    return Post.published.annotate(
        total_comments=Count('reviews', filter=models.Q(reviews__content_type=post_content_type))
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
