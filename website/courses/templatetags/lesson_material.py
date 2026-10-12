import re

import markdown
from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe


register = template.Library()

_unsafe_href = re.compile(r'href="(?!https?://|mailto:|/|#)[^"]*"', re.IGNORECASE)
_external_link = re.compile(r'<a href="(https?://[^"]+)">', re.IGNORECASE)


@register.filter
def render_markdown(value):
    """Render trusted course Markdown while escaping raw HTML and unsafe links."""
    if not value:
        return ''
    rendered = markdown.markdown(
        escape(str(value)),
        extensions=['fenced_code', 'tables'],
    )
    rendered = _unsafe_href.sub('href="#"', rendered)
    rendered = _external_link.sub(
        r'<a href="\1" target="_blank" rel="noopener noreferrer">',
        rendered,
    )
    return mark_safe(rendered)
