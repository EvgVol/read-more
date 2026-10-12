# Iteration 00 — Аудит и baseline

## Статус

DONE

## Изменённые файлы

- docs/architecture/learning-platform.md — фактическая архитектура, сущности, маршруты и риски.
- docs/iterations/iteration_00_report.md — отчёт и результаты baseline.

Исходный код приложения и архитектура в рамках Iteration 00 не изменялись.

## Реализовано

- Подтвержден стек: Django 4.2.4/Python 3.11, Daphne, PostgreSQL 13, Redis, Nginx, DRF, Celery-конфигурация.
- Подтверждены реальные модели курсов, уроков, legacy content, LessonMaterial, прогресса и журнала событий.
- Подтверждены маршруты каталога, trainer, progress endpoint и API.
- Зафиксировано отсутствие LessonBlock, версий блоков, квизов, Code Runner, flashcards, mastery и AI gateway.
- Проверена работа seed-команд и отсутствие дубликатов после повторного запуска.
- Выполнен browser smoke-check каталога через локальный браузер: каталог отображает курс «ML-инженер», ссылку курса и базовую навигацию.
- Подготовлен уточнённый план Iteration 01 ниже.

## Миграции и совместимость

- docker compose exec -T web python manage.py makemigrations --check --dry-run — No changes detected.
- Новые миграции не создавались.
- LessonMaterial и текущий прогресс не изменялись.
- seed_ml_materials использует update_or_create; после повторного seed: 1 курс, 7 модулей, 28 уроков, 28 материалов.
- Важный риск: seed_ml_course пересоздаёт модули и уроки; перенос в block-модель должен отдельно доказать сохранность прогресса.

## Тесты и smoke-check

| Команда / проверка | Результат | Количество | Примечание |
|---|---|---:|---|
| docker compose ps -a | PASSED | 5 active | db, cache, web, nginx, certbot работают; celery_worker не запущен |
| python manage.py check | PASSED | 0 issues | Django system check |
| python manage.py makemigrations --check --dry-run | PASSED | no changes | Миграций для аудита нет |
| python manage.py test courses --keepdb -v 1 | PASSED | 44 tests | Полный текущий набор courses |
| seed_ml_course + seed_ml_materials дважды | PASSED | 28 materials | Дубликаты не появились |
| Django Client /ru/courses/ | PASSED | HTTP 200 | Авторизованный smoke-check |
| Django Client trainer | PASSED | HTTP 200 | Рабочая область курса |
| Django Client lesson ?step=2 | PASSED | HTTP 200 | Теория и renderer доступны |
| Django Client /ru/api/courses/ | PASSED | HTTP 200 | DRF endpoint доступен |
| Nginx /static/css/course-learning.css | PASSED | HTTP 200 | 8896 bytes |
| Nginx visualization SVG | PASSED | HTTP 200 | 2985 bytes |

## Проверка критериев Iteration 00

- [x] Реальные модели и технологии задокументированы.
- [x] Маршруты каталога, курса, урока и API подтверждены.
- [x] Baseline-тесты воспроизводимы.
- [x] Текущие проблемы отделены от новых: legacy text model, отсутствие blocks/runner/assessments, неактивный worker.
- [x] Seed и миграционные проверки выполнены.
- [x] План миграции без потери данных сформулирован.
- [x] Результат проверен на запущенном приложении.
- [x] Визуальный baseline снят в локальном браузере: каталог с фильтрами, карточкой ML-инженера и основной навигацией; accessibility tree также проверен. Отдельный файл screenshot не экспортировался, но визуальная проверка выполнена в browser session.

## Уточнённый план Iteration 01

1. Добавить LessonBlock в website/courses/models/lesson_block.py с lesson, type, position, schema_version, content, config, published и timestamps.
2. Добавить серверный validator website/courses/services/lesson_blocks.py: разрешённые типы, payload по типу, непустой content, неотрицательная позиция, безопасный fallback для неизвестного типа.
3. Добавить миграцию в website/courses/migrations/ с индексами lesson/position и lesson/published/position, без удаления legacy-полей.
4. Добавить read-layer для trainer: сначала блоки, затем legacy adapter из LessonMaterial, если блоков нет.
5. Подключить только безопасные типы theory, image, summary, code_example; остальные типы пока возвращают fallback.
6. Добавить unit/integration тесты на CRUD, validation, ordering, permissions, legacy compatibility, empty/unknown types, idempotent import и сохранность LessonProgress.
7. Добавить docs/iterations/iteration_01_report.md и остановиться после проверки DoD.

## Риски и ограничения

- Не добавлялись зависимости, модели блоков и API: это намеренно отложено до подтверждения Iteration 01.
- Браузерный smoke-check и визуальный baseline выполнены для каталога; авторизованный trainer подтверждён Django Client, а не отдельной авторизованной browser-сессией.
- celery_worker описан в Compose, но не запускался в рамках baseline, поэтому фоновые задачи требуют отдельной проверки.

## Решение о переходе

GO — Iteration 00 завершена.  
Следующая контрольная точка: требуется подтверждение пользователя на реализацию Iteration 01.
