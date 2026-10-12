# Readable Learning Material Pilot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Переработать первый урок «Python для анализа данных» в удобный для последовательного изучения формат с короткими смысловыми секциями, callout-блоками, оглавлением, кодом, практикой и тремя учебными SVG-схемами.

**Architecture:** Сохранить `LessonMaterial` и Markdown как формат хранения. Добавить отдельный сервис подготовки учебного документа, который безопасно превращает Markdown в HTML и список пунктов оглавления; шаблон тренера отобразит результат и не будет смешивать рендеринг с логикой прогресса. Контент пилота будет отдельным lesson-specific blueprint в существующей management command, чтобы после проверки формат можно было распространить на остальные уроки.

**Tech Stack:** Django 4.x, Python 3.11, Python-Markdown, Django template tags, HTML/CSS, SVG, Docker Compose, Django `TestCase`.

**Spec:** `docs/superpowers/specs/2026-10-12-learning-material-readability-design.md`

## Global Constraints

- Не менять модель `LessonMaterial` на этапе пилота.
- Сохранить существующие пять этапов урока, прогресс и историю обучения.
- Не подключать внешние CDN или тяжёлый визуальный редактор.
- Все новые HTML-маркеры должны проходить экранирование и не ослаблять фильтрацию небезопасного Markdown.
- Учебные схемы должны быть локальными SVG с подписью и alt-текстом.
- Старые материалы без новых callout-маркеров должны продолжать корректно отображаться.
- Все production-кодовые изменения начинаются с падающего теста и заканчиваются полным запуском `courses` tests.

## Review Focus

- Небезопасный HTML, JavaScript и внешние ссылки в callout- и image-синтаксисе не должны попасть в итоговый HTML — тесты рендеринга в Task 1.
- Заголовки с одинаковым текстом и кириллицей должны получать стабильные уникальные anchor id — тесты slug/TOC в Task 1.
- Материал без новых маркеров должен оставаться читаемым и совместимым — legacy-тест в Task 1.
- Пустые разделы и изображения без alt-текста не должны создавать сломанные визуальные блоки — тесты контента в Task 2.
- Открытие этапов, отправка прогресса и история событий не должны измениться после появления TOC — view-тесты в Task 3.

## File Map

- Create: `website/courses/services/lesson_document.py` — безопасный рендеринг Markdown, callout-блоков и оглавления.
- Modify: `website/courses/templatetags/lesson_material.py` — тонкий template-tag API поверх сервиса документа.
- Modify: `website/templates/courses/manage/course/trainer.html` — TOC, semantic content sections, captions and document HTML.
- Modify: `website/static/css/course-learning.css` — styles for TOC, callouts, figures, section rhythm and code examples.
- Create: `website/static/images/courses/ml-inzhener/python/01-data-flow.svg` — file-to-result flow diagram.
- Create: `website/static/images/courses/ml-inzhener/python/02-boundaries.svg` — raw data/preprocessing/result boundaries diagram.
- Create: `website/static/images/courses/ml-inzhener/python/03-validation-loop.svg` — hypothesis-to-conclusion loop.
- Modify: `website/courses/management/commands/ml_theory.py` — readable pilot blueprint for the first lesson.
- Create: `website/courses/tests/test_lesson_document.py` — service-level security and formatting tests.
- Modify: `website/courses/tests/test_course_learning_assets.py` — static SVG and CSS contracts.
- Modify: `website/courses/tests/test_lesson_learning_template.py` — trainer view and TOC rendering tests.
- Modify: `docs/superpowers/sdd/2026-10-12-lesson-learning-flow/progress.md` — record the pilot implementation status if this ignored ledger is still used.

## Task 1: Add a safe lesson-document renderer

**Files:**
- Create: `website/courses/services/lesson_document.py`
- Modify: `website/courses/templatetags/lesson_material.py`
- Create: `website/courses/tests/test_lesson_document.py`

**Interfaces:**
- Consumes: raw Markdown text from `LessonMaterial.theory`.
- Produces: `LessonDocument`, a frozen dataclass with `html: str` and `toc: list[dict[str, str | int]]` fields. Each TOC item contains `title: str`, `anchor: str`, and `level: int`.
- Callout syntax: a block beginning with one of `:::important`, `:::remember`, `:::mistake`, `:::practice`, or `:::self-check`, ending with `:::`, becomes a semantic `<aside>` with a visible Russian label.
- Image policy: Markdown images are allowed only for local `/static/` or `/media/` paths and must have non-empty alt text; invalid images are rendered as safe text or omitted with no executable HTML.

- [ ] **Step 1: Write failing renderer tests**

Add tests with exact expectations for:

```python
def test_renders_callout_with_semantic_label_and_class():
    document = render_lesson_document(':::important\nНе меняйте test до финальной проверки.\n:::')
    assert '<aside' in document.html
    assert 'lesson-callout--important' in document.html
    assert 'Важно' in document.html

def test_builds_stable_unique_toc_ids_for_duplicate_headings():
    document = render_lesson_document('## Основы\n\n## Основы')
    assert [item['anchor'] for item in document.toc] == ['osnovy', 'osnovy-2']

def test_escapes_raw_html_and_rejects_external_image_sources():
    document = render_lesson_document(
        '<script>alert(1)</script>\n\n![схема](https://example.com/schema.svg)'
    )
    assert '<script>' not in document.html
    assert 'https://example.com/schema.svg' not in document.html

def test_legacy_markdown_without_callouts_still_renders():
    document = render_lesson_document('## Заголовок\n\nОбычный текст.')
    assert 'id="zagolovok"' in document.html
    assert 'Обычный текст.' in document.html
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run:

```bash
docker compose exec -T web python manage.py test courses.tests.test_lesson_document -v 2
```

Expected: FAIL because `render_lesson_document` and its document contract do not exist.

- [ ] **Step 3: Implement the minimal document service**

Implement `render_lesson_document(value)` in `lesson_document.py`:

1. Normalize empty input to an empty document with an empty TOC.
2. Parse callout blocks before Markdown conversion using a strict allowlist of five marker names.
3. Escape raw HTML before passing text to Python-Markdown.
4. Enable only the `fenced_code` and `tables` extensions; generate heading IDs and TOC entries with one deterministic local heading pass so the returned `toc` and rendered anchors cannot diverge.
5. Generate deterministic slug IDs for Cyrillic and Latin headings and append `-2`, `-3`, etc. for duplicates.
6. Sanitize image output so only `/static/` and `/media/` sources remain and alt text is present.
7. Return safe HTML plus plain TOC metadata; do not expose arbitrary Markdown-generated attributes.

Expose a template-tag function in `lesson_material.py` that lets the trainer template assign the document object without duplicating parsing logic.

- [ ] **Step 4: Run focused and existing Markdown tests**

Run:

```bash
docker compose exec -T web python manage.py test courses.tests.test_lesson_document courses.tests.test_lesson_material_views -v 1
```

Expected: all focused tests pass and existing escaping/link behavior remains green.

- [ ] **Step 5: Commit the renderer slice**

```bash
git add website/courses/services/lesson_document.py website/courses/templatetags/lesson_material.py website/courses/tests/test_lesson_document.py
git commit -m "feat: add safe lesson document renderer"
```

## Task 2: Rewrite the first lesson content and add educational diagrams

**Files:**
- Modify: `website/courses/management/commands/ml_theory.py`
- Create: `website/static/images/courses/ml-inzhener/python/01-data-flow.svg`
- Create: `website/static/images/courses/ml-inzhener/python/02-boundaries.svg`
- Create: `website/static/images/courses/ml-inzhener/python/03-validation-loop.svg`
- Create or modify: `website/courses/tests/test_ml_theory_pilot.py`

**Interfaces:**
- Consumes: lesson title `Python для анализа данных` and the existing seed command.
- Produces: Markdown theory with explicit headings, callout markers, local image references, at least one table, at least one fenced Python example, a guided practice checklist, and self-check questions.

- [ ] **Step 1: Write failing content-contract tests**

Create tests that call the existing theory builder/seed path and assert the first lesson contains:

```python
assert '## Как читать этот урок' in theory
assert ':::important' in theory
assert ':::practice' in theory
assert '```python' in theory
assert '| Этап | Что проверяем |' in theory
assert '/static/images/courses/ml-inzhener/python/01-data-flow.svg' in theory
assert 'alt="' in theory
assert theory.count('## ') >= 8
```

Also assert that the other lesson blueprints still return non-empty theory, so the pilot does not accidentally remove the remaining course content.

- [ ] **Step 2: Run the content tests and verify the pilot contract fails**

Run:

```bash
docker compose exec -T web python manage.py test courses.tests.test_ml_theory_pilot -v 2
```

Expected: FAIL because the current generic generated theory has neither the new callouts nor the pilot diagrams.

- [ ] **Step 3: Implement the first lesson blueprint**

Add a dedicated `PILOT_THEORY` or lesson-specific builder before the generic fallback. Keep the content beginner-first and preserve depth by splitting it into these sections:

1. `Как читать этот урок` — expected outcome and study route.
2. `Ментальная модель данных` — rows, columns, schema, target, feature.
3. `Путь данных от файла до результата` — first SVG and step list.
4. `Базовый Python для данных` — variables, collections, functions, types.
5. `Границы preprocessing` — second SVG, before/after examples, leakage warning.
6. `Надёжная функция преобразования` — fenced Python code and line-by-line explanation.
7. `Ошибки начинающего инженера` — callout blocks and a diagnostic table.
8. `Практика: маленький CSV-пайплайн` — checklist with expected intermediate outputs.
9. `Цикл проверки результата` — third SVG and validation sequence.
10. `Самопроверка и итог` — questions, answers hidden in the self-check stage, and transition to NumPy.

Use short paragraphs of 2–5 sentences, lists for enumerations, tables for comparisons, and a transition sentence at the end of every section. Keep all image references local and include descriptive Russian alt text.

- [ ] **Step 4: Implement the three SVG diagrams**

Each SVG must:

- use a viewBox and responsive width;
- contain a simple high-contrast flow with no tiny text;
- use the course palette already present in `course-learning.css`;
- include a `<title>` and `<desc>` matching the Markdown alt/caption;
- avoid external fonts, scripts, filters, or remote assets;
- remain understandable when printed or viewed on a narrow screen.

- [ ] **Step 5: Run the seed command and content tests**

Run:

```bash
docker compose exec -T web python manage.py seed_ml_materials
docker compose exec -T web python manage.py test courses.tests.test_ml_theory_pilot courses.tests.test_lesson_document -v 1
```

Expected: the first lesson receives the pilot theory, all 28 lesson materials remain present, and the renderer tests pass.

- [ ] **Step 6: Commit the content slice**

```bash
git add website/courses/management/commands/ml_theory.py website/static/images/courses/ml-inzhener/python website/courses/tests/test_ml_theory_pilot.py
git commit -m "content: restructure first Python lesson"
```

## Task 3: Add TOC, callouts, figures, and section transitions to the trainer

**Files:**
- Modify: `website/templates/courses/manage/course/trainer.html`
- Modify: `website/static/css/course-learning.css`
- Modify: `website/courses/tests/test_lesson_learning_template.py`
- Modify: `website/courses/tests/test_course_learning_assets.py`

**Interfaces:**
- Consumes: the lesson-document object from Task 1 and the pilot Markdown from Task 2.
- Produces: accessible reading layout with TOC links, callout blocks, figures, captions, and preserved progress controls.

- [ ] **Step 1: Write failing template and asset tests**

Extend the template tests to assert the rendered first lesson contains:

```python
assert 'Оглавление урока' in response.content.decode()
assert 'href="#kak-chitat-etot-urok"' in response.content.decode()
assert 'lesson-callout' in response.content.decode()
assert 'figure' in response.content.decode()
assert 'aria-label="Навигация по разделам урока"' in response.content.decode()
```

Add asset contracts that read the CSS/SVG files and assert the callout classes, figure styles, responsive rule, and all three SVG files exist.

- [ ] **Step 2: Run the focused view tests and verify they fail**

Run:

```bash
docker compose exec -T web python manage.py test courses.tests.test_lesson_learning_template courses.tests.test_course_learning_assets -v 2
```

Expected: FAIL because the current trainer renders only `active_content|render_markdown` and has no TOC or callout styling.

- [ ] **Step 3: Update the trainer template**

When the active step is theory:

1. Render a `nav` with heading `Оглавление урока` and links from the document TOC.
2. Render the document HTML inside the existing `.course-learning__reading` container.
3. Wrap figures with `figure`/`figcaption` semantics when the renderer emits local images.
4. Keep the current step title, completion form, history, adjacent lesson navigation, and CSRF behavior unchanged.
5. Add a visible “К началу теории” link after long sections only if the generated anchors make it useful; do not add redundant controls to every paragraph.

- [ ] **Step 4: Add responsive styles**

Add styles for:

- `.course-learning__toc` with a compact bordered surface;
- `.lesson-callout` and five modifier classes with icons or text labels, not color alone;
- `.lesson-material figure`, `figcaption`, and responsive SVG sizing;
- readable line length, paragraph spacing, list indentation, table overflow, and code wrapping;
- mobile layout where TOC precedes content and does not remain wider than the viewport;
- visible keyboard focus for TOC and internal section links.

Do not use large decorative cards or styling that hides the document hierarchy.

- [ ] **Step 5: Run the focused template tests**

Run:

```bash
docker compose exec -T web python manage.py test courses.tests.test_lesson_learning_template courses.tests.test_course_learning_assets -v 1
```

Expected: all tests pass and existing five-step/progress assertions remain green.

- [ ] **Step 6: Commit the trainer slice**

```bash
git add website/templates/courses/manage/course/trainer.html website/static/css/course-learning.css website/courses/tests/test_lesson_learning_template.py website/courses/tests/test_course_learning_assets.py
git commit -m "feat: improve lesson reading layout"
```

## Task 4: Verify browser behavior, accessibility, and performance

**Files:**
- Modify: `website/courses/tests/test_lesson_learning_template.py` only if a discovered regression needs a focused test.
- Modify: `docs/superpowers/sdd/2026-10-12-lesson-learning-flow/progress.md` with the verified pilot status.

- [ ] **Step 1: Rebuild and seed the local stack**

Run:

```bash
docker compose build web
docker compose up -d web nginx
docker compose exec -T web python manage.py seed_ml_materials
```

- [ ] **Step 2: Run the complete Django verification suite**

Run:

```bash
docker compose exec -T web python manage.py check
docker compose exec -T web python manage.py makemigrations courses --check --dry-run
docker compose exec -T web python manage.py test courses --keepdb -v 1
```

Expected: no system-check or migration output, and all course tests pass.

- [ ] **Step 3: Verify the authorized lesson route in a real browser**

Open the trainer with an authorized test session and verify:

- the page does not remain under the global loader;
- the first theory section and TOC are visible;
- each TOC link moves to the corresponding heading;
- callouts are readable without relying on color;
- SVG diagrams load with captions and no console/network errors;
- code and tables do not overflow horizontally on desktop or mobile;
- completing a theory step still records progress and history.

If Chrome DevTools MCP is unavailable, use the existing browser automation and Django test client for DOM/status checks, and report that limitation rather than claiming Core Web Vitals.

- [ ] **Step 4: Compare pilot performance to the pre-pilot baseline**

Measure the authorized trainer lesson with the same Django `CaptureQueriesContext` and response-size script used by `test_course_learning_performance.py`. Record:

- status code;
- SQL query count;
- server response time;
- uncompressed and gzip response size;
- number and size of SVG assets.

Keep the pilot only if the content improvements do not introduce a material regression. If SVG or TOC additions increase the response unexpectedly, move large visual data to static files and keep only references in HTML.

- [ ] **Step 5: Update the progress ledger and commit verification**

Record the actual test commands and browser observations in the ignored progress ledger, then run:

```bash
git diff --check
git status --short
```

Commit only the pilot files that belong to this plan:

```bash
git add docs/superpowers/sdd/2026-10-12-lesson-learning-flow/progress.md
git commit -m "test: verify readable lesson pilot"
```

## Handoff to the next iteration

After Task 4, stop and review the pilot manually before changing the other three Python lessons. Compare whether students can answer the first lesson’s self-check questions and follow the practice without opening the source code. Only then reuse the content template for NumPy, Pandas, and Git/Jupyter; do not mass-regenerate all 28 lessons before the pilot format is accepted.
