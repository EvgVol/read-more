# Lesson Learning Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Сделать страницу курса ML-инженера удобной для последовательного обучения с сохранением текущего шага, статусов уроков, общего прогресса и истории действий.

**Architecture:** Добавить две связанные модели `LessonProgress` и `LessonProgressEvent`. Сервер будет хранить текущее состояние и обрабатывать переходы через защищённый POST-view, а шаблон будет показывать один из пяти учебных шагов, навигацию, статусы и историю. Существующие материалы и безопасный Markdown-фильтр останутся источником контента.

**Tech Stack:** Django models/migrations/class-based views, Django templates, Bootstrap-классы существующей темы, локальный CSS, Django TestCase/Client, Docker Compose.

**Spec:** `docs/superpowers/specs/2026-10-12-lesson-learning-flow-design.md`

## Global Constraints

- Существующий контент не переписывается и не теряется.
- Прогресс хранится отдельно для каждого пользователя и урока.
- Гостевой пользователь не должен создавать или видеть чужой прогресс.
- Обновление прогресса выполняется обычным POST-запросом с CSRF-защитой.
- Завершение пятого этапа переводит урок в `completed` и фиксирует `completed_at`.
- JavaScript может улучшать интерфейс, но основной сценарий работает без него.
- Markdown продолжает проходить через существующую безопасную обработку.

## Review Focus

- Повторная отправка `complete_step` не должна создавать некорректный переход или сбрасывать завершённый урок — тест в Task 2.
- POST с чужим `user_id`, чужим уроком или уроком из другого курса не должен изменять состояние — тест в Task 3.
- Завершённый урок после повторного открытия должен оставаться завершённым, а история должна сохраняться — тест в Task 3.
- Урок без `LessonMaterial` должен отображать empty state и не становиться завершённым автоматически — тест в Task 4.
- Длинная теория и таблицы/код должны оставаться читаемыми на узком экране и не ломать безопасный Markdown — тест шаблонного контракта в Task 5 и HTTP-проверка в Task 6.

### Task 1: Модели состояния и история прогресса

**Files:**
- Create: `website/courses/models/lesson_progress.py`
- Modify: `website/courses/models/__init__.py`
- Modify: `website/courses/models/lesson_material.py` only if model import conventions require it
- Create: `website/courses/migrations/0009_lessonprogress.py`
- Test: `website/courses/tests/test_lesson_progress_models.py`

**Interfaces:**
- Produces `LessonProgress(user, lesson, status, current_step, started_at, last_opened_at, completed_at)`.
- Produces `LessonProgressEvent(progress, event_type, step, created_at)`.
- Produces constants/status choices that views can import without duplicating string literals.

- [ ] **Step 1: Write the failing model tests**

```python
def test_progress_is_unique_per_user_and_lesson(self):
    LessonProgress.objects.create(user=self.user, lesson=self.lesson)
    with self.assertRaises(IntegrityError):
        LessonProgress.objects.create(user=self.user, lesson=self.lesson)

def test_progress_event_is_deleted_with_progress(self):
    progress = LessonProgress.objects.create(user=self.user, lesson=self.lesson)
    LessonProgressEvent.objects.create(
        progress=progress, event_type=LessonProgressEvent.EventType.STARTED,
    )
    progress.delete()
    self.assertFalse(LessonProgressEvent.objects.exists())
```

Также проверить значения по умолчанию: `status=not_started`, `current_step=1`, nullable dates и допустимый диапазон этапов через `CheckConstraint`.

- [ ] **Step 2: Run the model tests and verify failure**

Run:

```bash
docker compose build web && docker compose up -d web
docker compose exec -T web python manage.py test courses.tests.test_lesson_progress_models --keepdb -v 1
```

Expected: FAIL because the progress models and migration do not exist.

- [ ] **Step 3: Implement the models and migration**

`LessonProgress` must have a unique constraint on `user` and `lesson`, indexes for user/status and lesson, `updated=auto_now`, and `on_delete=CASCADE`. `LessonProgressEvent` must use a foreign key to progress with `related_name='events'`, event choices `started`, `section_completed`, `lesson_completed`, `reopened`, nullable `step`, and indexes on `(progress, created_at)` and `(event_type, created_at)`.

Register both models through the existing courses model import path, run `makemigrations courses`, and inspect the generated migration before applying it.

- [ ] **Step 4: Run model tests and migration checks**

Run:

```bash
docker compose exec -T web python manage.py migrate
docker compose exec -T web python manage.py test courses.tests.test_lesson_progress_models --keepdb -v 1
docker compose exec -T web python manage.py makemigrations courses --check --dry-run
```

Expected: model tests pass and the final command reports no changes detected.

- [ ] **Step 5: Commit**

```bash
git add website/courses/models website/courses/migrations website/courses/tests/test_lesson_progress_models.py
git commit -m "feat: add lesson progress history models"
```

### Task 2: Progress service and deterministic state transitions

**Files:**
- Create: `website/courses/services/lesson_progress.py`
- Modify: `website/courses/tests/test_lesson_progress_models.py`
- Create: `website/courses/tests/test_lesson_progress_service.py`

**Interfaces:**
- `get_or_start_progress(*, user, lesson) -> LessonProgress` creates the row and `started` event only once, updates `last_opened_at` on later opens, and emits `reopened` only when a completed lesson is opened again.
- `complete_step(*, user, lesson, step: int) -> LessonProgress` validates the current step, advances at most one step, emits `section_completed`, and emits `lesson_completed` exactly once for step 5.
- `course_progress(*, user, course) -> dict` returns `total_lessons`, `completed_lessons`, `percent`, and `last_progress`.

- [ ] **Step 1: Write failing service tests**

Cover first open, repeated open, sequential completion 1→5, invalid forward jump, idempotent repeated completion, course percentage, and completed-lesson reopen without reset.

```python
def test_complete_step_advances_once_and_is_idempotent(self):
    progress = get_or_start_progress(user=self.user, lesson=self.lesson)
    complete_step(user=self.user, lesson=self.lesson, step=1)
    complete_step(user=self.user, lesson=self.lesson, step=1)
    progress.refresh_from_db()
    self.assertEqual(progress.current_step, 2)
    self.assertEqual(
        progress.events.filter(event_type='section_completed', step=1).count(),
        1,
    )
```

- [ ] **Step 2: Run service tests and verify failure**

Run:

```bash
docker compose exec -T web python manage.py test courses.tests.test_lesson_progress_service --keepdb -v 1
```

Expected: FAIL because the service functions do not exist.

- [ ] **Step 3: Implement atomic service functions**

Use `transaction.atomic()` and `select_for_update()` for transitions. Treat a request for an already completed step as a no-op. Reject a step greater than `current_step` with `ValidationError`. When step 5 is completed, set `status=completed`, `current_step=5`, `completed_at=timezone.now()`, and create one completion event. Do not accept a user or course identifier from a browser payload.

- [ ] **Step 4: Run service tests and full model regression**

Run:

```bash
docker compose exec -T web python manage.py test courses.tests.test_lesson_progress_models courses.tests.test_lesson_progress_service --keepdb -v 1
```

Expected: all tests pass with no duplicate events and no state reset.

- [ ] **Step 5: Commit**

```bash
git add website/courses/services website/courses/tests/test_lesson_progress_service.py website/courses/tests/test_lesson_progress_models.py
git commit -m "feat: add lesson progress transitions"
```

### Task 3: Trainer view, navigation and POST endpoint

**Files:**
- Modify: `website/courses/views/generic/detail.py`
- Create: `website/courses/views/progress.py`
- Modify: `website/courses/urls.py`
- Create: `website/courses/tests/test_lesson_progress_views.py`

**Interfaces:**
- `CourseTrainerView` adds `lesson_steps`, `active_step`, `progress`, `course_progress`, `previous_lesson`, `next_lesson`, and `recent_events` to context.
- `LessonProgressUpdateView.post()` accepts only `action=complete_step` and `step`, calls `complete_step`, and redirects to the active lesson with `step` query parameter or the next lesson after finishing step 5.

- [ ] **Step 1: Write failing view tests**

Test authenticated first open, context values, step completion POST, invalid step, guest redirect, enrolled-user authorization, cross-module lesson 404, and cross-user modification rejection.

```python
def test_first_lesson_open_creates_progress_and_exposes_steps(self):
    response = self.client.get(self.lesson_url)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.context['active_step'], 1)
    self.assertEqual(len(response.context['lesson_steps']), 5)
    self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=self.lesson).exists())

def test_complete_step_post_redirects_to_next_step(self):
    response = self.client.post(
        self.progress_url,
        {'action': 'complete_step', 'step': 1},
    )
    self.assertEqual(response.status_code, 302)
    self.assertIn('step=2', response.url)
```

- [ ] **Step 2: Run the view tests and verify failure**

Run:

```bash
docker compose exec -T web python manage.py test courses.tests.test_lesson_progress_views --keepdb -v 1
```

Expected: FAIL because context keys, URL and POST view are not implemented.

- [ ] **Step 3: Implement view context and route**

Create a fixed server-side list of five step descriptors: `objectives`, `theory`, `practice`, `self_check`, `resources`, with labels and template field names. Resolve `step` only from the range 1–5. For a missing query parameter, use persisted `current_step`; for a completed lesson, use step 5. Compute previous/next lesson from the ordered lessons of the course, not from an untrusted URL value.

Add a route:

```python
path(
    'course/<slug:slug>/trainer/<int:module_id>/lesson/<int:lesson_id>/progress/',
    LessonProgressUpdateView.as_view(),
    name='course_trainer_lesson_progress',
)
```

The POST view must reuse the same course access queryset and verify that the lesson belongs to the selected module/course before calling the service.

- [ ] **Step 4: Run view tests and route regression**

Run:

```bash
docker compose exec -T web python manage.py test courses.tests.test_lesson_progress_views courses.tests.test_lesson_material_views --keepdb -v 1
```

Expected: new progress behavior and all existing material access tests pass.

- [ ] **Step 5: Commit**

```bash
git add website/courses/views website/courses/urls.py website/courses/tests/test_lesson_progress_views.py
git commit -m "feat: add lesson progress views"
```

### Task 4: Progressive lesson template and course navigation

**Files:**
- Modify: `website/templates/courses/manage/course/trainer.html`
- Modify: `website/templates/courses/manage/course/lesson_material.html`
- Create: `website/templates/courses/manage/course/_lesson_sidebar.html`
- Create: `website/templates/courses/manage/course/_lesson_progress_controls.html`
- Create: `website/templates/courses/manage/course/_lesson_history.html`
- Modify: `website/courses/tests/test_lesson_material_views.py`
- Create: `website/courses/tests/test_lesson_learning_template.py`

**Interfaces:**
- Consumes the context contract from Task 3.
- Renders only the selected step content; it never trusts a field name from the request.
- Uses `{% csrf_token %}` in the progress form and standard anchor links for previous/next navigation.

- [ ] **Step 1: Write failing template tests**

Assert that the response contains the five step labels, `Шаг 1 из 5`, the course percentage, the lesson sidebar, the completion form with CSRF token, previous/next navigation, status text, and recent-history entries. Assert that when `material=None`, an empty state is shown and no completion action is offered.

- [ ] **Step 2: Run template tests and verify failure**

Run:

```bash
docker compose exec -T web python manage.py test courses.tests.test_lesson_learning_template --keepdb -v 1
```

Expected: FAIL because the current template renders every material section at once and has no progress controls.

- [ ] **Step 3: Implement the progressive template**

Replace the single long material include with a step card that selects the field from the server-provided step descriptor. Add:

- module breadcrumb and course percentage;
- sidebar with module/lesson statuses and accessible text labels;
- five-step progress indicator using `aria-current` and visible text;
- current section heading and rendered Markdown;
- POST form for `complete_step`;
- previous/next lesson links and step navigation;
- history list with localized `date` formatting;
- empty state for missing material.

Use semantic `nav`, `main`, `aside`, `ol`, `button`, and `form` elements. The completion control must remain keyboard accessible and must not depend on color alone.

- [ ] **Step 4: Run template tests and all course tests**

Run:

```bash
docker compose exec -T web python manage.py test courses --keepdb -v 1
```

Expected: all existing and new tests pass.

- [ ] **Step 5: Commit**

```bash
git add website/templates/courses/manage/course website/courses/tests
git commit -m "feat: add progressive lesson interface"
```

### Task 5: Readability, responsive styles and history presentation

**Files:**
- Create: `website/static/css/course-learning.css`
- Modify: `website/templates/main.html` or the existing course base include to load `course-learning.css`
- Modify: `website/templates/courses/manage/course/trainer.html` only for stable class names and landmarks
- Create: `website/courses/tests/test_course_learning_assets.py`

**Interfaces:**
- CSS classes use the `course-learning__` prefix to avoid collisions with the existing theme.
- No dependency on a new frontend framework or build step.

- [ ] **Step 1: Write failing asset/template contract tests**

Check that the lesson page includes `/static/css/course-learning.css`, the main learning landmarks, classes for the sidebar/content/history, and responsive breakpoint rules are present in the served stylesheet.

- [ ] **Step 2: Run the asset tests and verify failure**

Run:

```bash
docker compose exec -T web python manage.py test courses.tests.test_course_learning_assets --keepdb -v 1
```

Expected: FAIL because the new stylesheet and class contract do not exist.

- [ ] **Step 3: Implement readable styles**

Add a constrained reading column, `1.65` line-height, comfortable paragraph spacing, distinct `h2/h3`, readable code blocks with horizontal overflow, table overflow on small screens, visible focus outlines, status badges with text, sticky desktop sidebar, and a single-column mobile layout below `992px`. Do not override the global theme broadly; scope all rules beneath `.course-learning`.

- [ ] **Step 4: Run asset tests and inspect the real served CSS**

Run:

```bash
docker compose build web && docker compose up -d web
docker compose exec -T web python manage.py test courses.tests.test_course_learning_assets --keepdb -v 1
curl -sS -o /dev/null -w 'learning-css=%{http_code} %{content_type}\n' http://127.0.0.1:18080/static/css/course-learning.css
```

Expected: test passes and CSS returns `200 text/css`.

- [ ] **Step 5: Commit**

```bash
git add website/static/css/course-learning.css website/templates
git commit -m "style: improve course learning readability"
```

### Task 6: End-to-end Docker verification and final review

**Files:**
- Modify: `website/courses/tests/test_ml_course_end_to_end.py` if route/count assertions need the new progress route
- No new production files unless verification finds a concrete defect.

- [ ] **Step 1: Run the complete test suite**

```bash
docker compose exec -T web python manage.py test courses --keepdb -v 1
docker compose exec -T web python manage.py check
docker compose exec -T web python manage.py makemigrations courses --check --dry-run
```

Expected: all tests pass, Django reports no issues, and no pending migration changes exist.

- [ ] **Step 2: Verify database state and seed compatibility**

```bash
docker compose exec -T web python manage.py seed_ml_course
docker compose exec -T web python manage.py seed_ml_materials
docker compose exec -T web python manage.py shell -c "from courses.models import Course; from courses.models.lesson_material import LessonMaterial; c=Course.objects.get(slug='ml-inzhener'); print(c.modules.count(), sum(m.lessons.count() for m in c.modules.all()), LessonMaterial.objects.filter(lesson__module__course=c).count())"
```

Expected: `7 28 28`; course seeding must not delete progress for unrelated users and the material seed must remain idempotent.

- [ ] **Step 3: Verify HTTP/static behavior and logs**

```bash
curl -sS -o /dev/null -w 'catalog=%{http_code}\n' http://127.0.0.1:18080/ru/courses/
curl -sS -o /dev/null -w 'learning-css=%{http_code} %{content_type}\n' http://127.0.0.1:18080/static/css/course-learning.css
docker compose ps
docker compose logs --tail=100 web nginx | rg -i 'traceback|template syntax|internal server error| 500 ' || true
```

Expected: catalog and CSS return 200, all required containers are running, and no matching server errors appear.

- [ ] **Step 4: Review the complete diff**

Run `git diff --check`, inspect the migration, service transitions, access checks, template context and responsive CSS. Confirm unrelated existing changes (`.gitignore`, Docker/nginx configuration and static assets) are not staged.

- [ ] **Step 5: Commit verification-only fixes if needed**

If a concrete defect is found, add a failing regression test first, fix it, rerun the complete suite, and commit with a focused message. Otherwise leave the implementation commits unchanged.

