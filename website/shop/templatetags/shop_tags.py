from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown
import html

from ..models import Category

register = template.Library()


@register.inclusion_tag('shop/includes/categories.html')
def show_categories():
    categories = Category.objects.annotate(
        num_products=Count('products')
    ).filter(num_products__gt=0)\
     .order_by('-num_products')
    return {'categories': categories}


@register.filter(name='markdown')
def markdown_format(text):
    """User-authored Markdown, raw HTML escaped (see blog_tags)."""
    return mark_safe(markdown.markdown(html.escape(text)))