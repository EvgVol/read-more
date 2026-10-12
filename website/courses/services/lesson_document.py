"""Render structured lesson Markdown for the learning interface."""

from dataclasses import dataclass
import html
import re

import markdown
from django.utils.html import escape
from django.utils.safestring import mark_safe


@dataclass(frozen=True)
class LessonDocument:
    html: str
    toc: list[dict[str, str | int]]


_CALLOUT_RE = re.compile(
    r'^:::(important|remember|mistake|practice|self-check)\s*\n'
    r'(.*?)^:::\s*$',
    re.MULTILINE | re.DOTALL,
)
_HEADING_RE = re.compile(r'^(#{2,6})\s+(.+?)\s*#*\s*$')
_IMAGE_RE = re.compile(r'<img\b[^>]*>', re.IGNORECASE)
_ATTRIBUTE_RE = re.compile(
    r'(?P<name>alt|src)\s*=\s*["\'](?P<value>[^"\']*)["\']',
    re.IGNORECASE,
)
_UNSAFE_HREF_RE = re.compile(
    r'href="(?!https?://|mailto:|/|#)[^"]*"',
    re.IGNORECASE,
)
_EXTERNAL_LINK_RE = re.compile(
    r'<a href="(https?://[^"]+)">',
    re.IGNORECASE,
)

_CALLOUT_LABELS = {
    'important': 'Важно',
    'remember': 'Запомните',
    'mistake': 'Типичная ошибка',
    'practice': 'Практика',
    'self-check': 'Проверка себя',
}
_TRANSLITERATION = str.maketrans({
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e',
    'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
    'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
    'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts',
    'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '',
    'э': 'e', 'ю': 'yu', 'я': 'ya',
})


def _slugify_heading(title: str) -> str:
    slug = title.strip().lower().translate(_TRANSLITERATION)
    slug = re.sub(r'[^a-z0-9]+', '-', slug).strip('-')
    return slug or 'section'


def _extract_callouts(source: str) -> tuple[str, list[str]]:
    callout_html: list[str] = []

    def replace(match):
        kind = match.group(1)
        body = _render_markdown_fragment(match.group(2).strip())
        index = len(callout_html)
        label = _CALLOUT_LABELS[kind]
        callout_html.append(
            f'<aside class="lesson-callout lesson-callout--{kind}" role="note">'
            f'<strong class="lesson-callout__label">{label}</strong>'
            f'<div class="lesson-callout__body">{body}</div>'
            '</aside>'
        )
        return f'\n@@LESSON_CALLOUT_{index}@@\n'

    return _CALLOUT_RE.sub(replace, source), callout_html


def _extract_headings(source: str) -> tuple[str, list[dict[str, str | int]], list[str]]:
    headings: list[dict[str, str | int]] = []
    placeholders: list[str] = []
    seen: dict[str, int] = {}
    output: list[str] = []
    in_fence = False

    for line in source.splitlines():
        if line.strip().startswith('```'):
            in_fence = not in_fence
            output.append(line)
            continue
        match = None if in_fence else _HEADING_RE.match(line)
        if not match:
            output.append(line)
            continue

        level = len(match.group(1))
        title = match.group(2).strip()
        base_anchor = _slugify_heading(title)
        seen[base_anchor] = seen.get(base_anchor, 0) + 1
        anchor = base_anchor if seen[base_anchor] == 1 else f'{base_anchor}-{seen[base_anchor]}'
        index = len(placeholders)
        placeholders.append(
            f'<h{level} id="{anchor}">{escape(title)}</h{level}>'
        )
        headings.append({'title': title, 'anchor': anchor, 'level': level})
        output.append(f'@@LESSON_HEADING_{index}@@')

    return '\n'.join(output), headings, placeholders


def _render_markdown_fragment(value: str) -> str:
    rendered = markdown.markdown(
        escape(value),
        extensions=['fenced_code', 'tables'],
    )
    return _sanitize_html(rendered)


def _sanitize_image(match: re.Match) -> str:
    attributes = {
        item.group('name').lower(): html.unescape(item.group('value'))
        for item in _ATTRIBUTE_RE.finditer(match.group(0))
    }
    source = attributes.get('src', '')
    alt = attributes.get('alt', '').strip()
    if not alt or not source.startswith(('/static/', '/media/')):
        return ''
    return (
        '<figure class="lesson-material__figure">'
        f'<img src="{escape(source)}" alt="{escape(alt)}">'
        f'<figcaption>{escape(alt)}</figcaption>'
        '</figure>'
    )


def _sanitize_html(rendered: str) -> str:
    rendered = _IMAGE_RE.sub(_sanitize_image, rendered)
    rendered = _UNSAFE_HREF_RE.sub('href="#"', rendered)
    return _EXTERNAL_LINK_RE.sub(
        r'<a href="\1" target="_blank" rel="noopener noreferrer">',
        rendered,
    )


def render_lesson_document(value: str | None) -> LessonDocument:
    """Render safe lesson Markdown and expose its heading navigation."""
    if not value:
        return LessonDocument(html='', toc=[])

    source, callouts = _extract_callouts(str(value))
    source, toc, headings = _extract_headings(source)
    rendered = _render_markdown_fragment(source)
    for index, replacement in enumerate(callouts):
        rendered = rendered.replace(f'@@LESSON_CALLOUT_{index}@@', replacement)
    for index, replacement in enumerate(headings):
        rendered = rendered.replace(f'@@LESSON_HEADING_{index}@@', replacement)
    return LessonDocument(html=mark_safe(rendered), toc=toc)
