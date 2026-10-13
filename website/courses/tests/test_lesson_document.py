from html import unescape

from django.test import SimpleTestCase

from courses.services.lesson_document import render_lesson_document


class LessonDocumentTests(SimpleTestCase):
    def test_renders_callout_with_semantic_label_and_class(self):
        document = render_lesson_document(
            ':::important\nНе меняйте test до финальной проверки.\n:::'
        )

        self.assertIn('<aside', document.html)
        self.assertIn('lesson-callout--important', document.html)
        self.assertIn('Важно', document.html)

    def test_builds_stable_unique_toc_ids_for_duplicate_headings(self):
        document = render_lesson_document('## Основы\n\n## Основы')

        self.assertEqual(
            [item['anchor'] for item in document.toc],
            ['osnovy', 'osnovy-2'],
        )

    def test_escapes_raw_html_and_rejects_external_image_sources(self):
        document = render_lesson_document(
            '<script>alert(1)</script>\n\n'
            '![схема](https://example.com/schema.svg)'
        )

        self.assertNotIn('<script>', document.html)
        self.assertNotIn('https://example.com/schema.svg', document.html)

    def test_legacy_markdown_without_callouts_still_renders(self):
        document = render_lesson_document('## Заголовок\n\nОбычный текст.')

        self.assertIn('id="zagolovok"', document.html)
        self.assertIn('Обычный текст.', document.html)

    def test_heading_prefix_keeps_block_anchors_unique(self):
        document = render_lesson_document('## Основы', heading_prefix='block-20-')

        self.assertEqual(document.toc[0]['anchor'], 'block-20-osnovy')

    def test_fenced_code_is_not_double_escaped(self):
        # The parser escapes code once; the pre-escape pass must not add a
        # second level, otherwise the browser shows an entity, not ">"
        source = "amount = '120.50'\nassert amount > 0\n"
        document = render_lesson_document('```python\n' + source + '```\n')
        html = document.html

        self.assertIn('<pre><code class="language-python">', html)
        code_start = html.index('<code')
        inner = html[html.index('>', code_start) + 1: html.rindex('</code>')]
        # After exactly one HTML decode the code must match the source
        # verbatim; a double escape would leave a literal entity behind.
        self.assertEqual(unescape(inner).strip(), source.strip())

    def test_inline_code_is_not_double_escaped(self):
        document = render_lesson_document('Порог `value > 0` обязателен.')
        html = document.html

        self.assertIn('<code>value', html)
        inner = html[html.index('<code>') + 6: html.rindex('</code>')]
        self.assertEqual(unescape(inner), 'value > 0')
