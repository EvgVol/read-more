from django import template
from django.utils.html import escape


register = template.Library()


@register.filter
def model_name(obj):
    try:
        return obj._meta.model_name
    except AttributeError:
        return None


@register.filter
def technology_logo(name):
    """Return the local static logo path for a technology name."""
    return f'/static/images/courses/ml-inzhener/logos/{escape(name.lower())}.svg'