import re

from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.utils.safestring import mark_safe

from courses.models.lesson_block import LessonBlock
from courses.services.lesson_document import LessonDocument, render_lesson_document


_LOCAL_ASSET_PREFIXES = ('/static/', '/media/')
_LANGUAGE_RE = re.compile(r'^[a-zA-Z0-9_+#.-]{1,32}$')
_BLOCK_CLASS_RE = re.compile(r'[^a-z0-9-]+')

_BLOCK_LABELS = {
    LessonBlock.Type.THEORY: 'Теоретический блок',
    LessonBlock.Type.IMAGE: 'Иллюстрация',
    LessonBlock.Type.CODE_EXAMPLE: 'Пример кода',
    LessonBlock.Type.SUMMARY: 'Итоговый блок',
}


def _require_mapping(value, field):
    if not isinstance(value, dict):
        raise ValidationError({field: 'Должен быть JSON-объект.'})


def validate_lesson_block_payload(*, block_type, content, config, schema_version):
    """Validate known block contracts while allowing future types to fallback."""
    errors = {}
    if schema_version != 1:
        errors['schema_version'] = 'Поддерживается только schema_version=1.'
    _require_mapping(content, 'content')
    _require_mapping(config, 'config')

    if block_type in (LessonBlock.Type.THEORY, LessonBlock.Type.SUMMARY):
        if not isinstance(content.get('markdown'), str) or not content['markdown'].strip():
            errors['content'] = 'Для текстового блока нужен непустой markdown.'
    elif block_type == LessonBlock.Type.IMAGE:
        source = content.get('src')
        alt = content.get('alt')
        if not isinstance(source, str) or not source.startswith(_LOCAL_ASSET_PREFIXES):
            errors['content'] = 'Изображение должно ссылаться на локальный static/media asset.'
        if not isinstance(alt, str) or not alt.strip():
            errors['content'] = 'Изображение должно иметь непустой alt-текст.'
    elif block_type == LessonBlock.Type.CODE_EXAMPLE:
        if not isinstance(content.get('code'), str) or not content['code'].strip():
            errors['content'] = 'Для code_example нужен непустой code.'
        language = content.get('language', 'text')
        if not isinstance(language, str) or not _LANGUAGE_RE.fullmatch(language):
            errors['content'] = 'language содержит недопустимые символы.'

    if errors:
        raise ValidationError(errors)


def _render_block(block):
    content = block.content
    if block.type in (LessonBlock.Type.THEORY, LessonBlock.Type.SUMMARY):
        return content['markdown']
    if block.type == LessonBlock.Type.IMAGE:
        return f"![{content['alt']}]({content['src']})"
    if block.type == LessonBlock.Type.CODE_EXAMPLE:
        return f"```{content.get('language', 'text')}\n{content['code']}\n```"
    return (
        ':::important\n'
        'Этот блок подготовлен в новой версии формата и пока отображается в безопасном fallback-режиме.\n'
        ':::'
    )


def render_lesson_blocks(blocks):
    """Convert published blocks to legacy-safe Markdown for the current renderer."""
    return '\n\n'.join(_render_block(block) for block in blocks)


def get_published_lesson_blocks(lesson):
    """Return blocks from the view prefetch when available, otherwise query them."""
    blocks = getattr(lesson, 'published_lesson_blocks', None)
    if blocks is None:
        blocks = lesson.blocks.filter(published=True)
    return list(blocks)


def render_lesson_blocks_document(blocks) -> LessonDocument:
    """Render each published block as a labelled, independently styled document fragment."""
    fragments = []
    toc = []
    for block in blocks:
        block_type = str(block.type)
        class_suffix = block_type.lower().replace('_', '-')
        class_suffix = _BLOCK_CLASS_RE.sub('-', class_suffix).strip('-') or 'unknown'
        label = _BLOCK_LABELS.get(block_type, 'Дополнительный материал')
        document = render_lesson_document(
            _render_block(block),
            heading_prefix=f'block-{block.position}-',
        )
        fragments.append(
            f'<article class="lesson-block lesson-block--{class_suffix}" '
            f'data-block-type="{escape(block_type)}" aria-label="{escape(label)}">'
            f'{document.html}</article>'
        )
        # The structured lesson already has its own meaningful block boundary.
        # Keep only the first heading per block so the TOC remains a study path
        # instead of repeating labels such as "Теория" and "Самопроверка".
        if document.toc:
            toc.append(document.toc[0])
    return LessonDocument(html=mark_safe('\n'.join(fragments)), toc=toc)


def get_lesson_stage_content(lesson, stage, material):
    """Read blocks for theory and preserve legacy fields for all other stages."""
    legacy_content = getattr(material, stage, '') if material else ''
    if stage != 'theory':
        return legacy_content

    blocks = get_published_lesson_blocks(lesson)
    return render_lesson_blocks(blocks) if blocks else legacy_content
