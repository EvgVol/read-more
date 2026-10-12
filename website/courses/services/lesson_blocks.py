import re

from django.core.exceptions import ValidationError

from courses.models.lesson_block import LessonBlock


_LOCAL_ASSET_PREFIXES = ('/static/', '/media/')
_LANGUAGE_RE = re.compile(r'^[a-zA-Z0-9_+#.-]{1,32}$')


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


def get_lesson_stage_content(lesson, stage, material):
    """Read blocks for theory and preserve legacy fields for all other stages."""
    legacy_content = getattr(material, stage, '') if material else ''
    if stage != 'theory':
        return legacy_content

    blocks = getattr(lesson, 'published_lesson_blocks', None)
    if blocks is None:
        blocks = lesson.blocks.filter(published=True)
    blocks = list(blocks)
    return render_lesson_blocks(blocks) if blocks else legacy_content
