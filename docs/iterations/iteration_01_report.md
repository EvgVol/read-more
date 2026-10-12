# Iteration 01 — Универсальная модель блоков

## Статус

DONE

## Изменённые файлы

- website/courses/models/lesson_block.py — модель LessonBlock.
- website/courses/migrations/0010_lessonblock.py — обратимая additive-миграция.
- website/courses/services/lesson_blocks.py — payload validation, rendering и legacy read adapter.
- website/courses/views/generic/detail.py — prefetch опубликованных блоков и подключение theory к trainer.
- website/courses/tests/test_lesson_blocks.py — unit/integration/security tests.
- website/courses/tests/test_lesson_learning_template.py — trainer regression test.

## Реализовано

- Добавлен LessonBlock с lesson, type, position, schema_version, content, config, published и timestamps.
- Добавлены уникальный порядок блоков внутри урока и индекс для опубликованной последовательности.
- Поддержаны типы theory, image, summary и code_example.
- Неизвестный тип не ломает страницу и отображается безопасным fallback-блоком без вывода произвольного payload.
- Для image разрешены только локальные /static/ и /media/ источники; alt обязателен.
- Для code_example проверяются непустой код и безопасный формат language.
- Theory читает опубликованные блоки, если они существуют; при отсутствии опубликованных блоков используется прежний LessonMaterial.theory.
- Practice, self_check и resources продолжают читаться из legacy LessonMaterial.
- Блоки загружаются через Prefetch без N+1-запросов.
- Старый trainer и уроки без блоков продолжают открываться.

## Миграции и совместимость

- Migration 0010 применена в контейнере.
- python manage.py makemigrations courses --check --dry-run — No changes detected.
- Существующие LessonMaterial и LessonProgress не изменяются.
- seed_ml_course и seed_ml_materials не создают LessonBlock автоматически; текущие 28 уроков используют legacy fallback до содержательной миграции.
- После seed: 1 курс, 7 модулей, 28 уроков, 28 материалов, 0 блоков.

## Тесты

| Команда | Результат | Количество | Примечание |
|---|---|---:|---|
| python manage.py check | PASSED | 0 issues | Django system check |
| python manage.py makemigrations courses --check --dry-run | PASSED | no changes | Модель и миграция синхронизированы |
| python manage.py test courses --keepdb -v 1 | PASSED | 50 tests | Полный набор courses |
| test_lesson_blocks | PASSED | 5 tests | payload, fallback, ordering, legacy, external image |
| lesson learning template | PASSED | 4 tests | опубликованный блок в trainer |
| seed_ml_course + seed_ml_materials | PASSED | 28 materials | Дубликаты не создаются |
| Nginx /static/css/course-learning.css | PASSED | HTTP 200 | 8896 bytes |

## Проверка критериев приёмки

- [x] Модель блоков создана.
- [x] Payload валидируется по type/schema_version.
- [x] Неизвестный тип имеет безопасный fallback.
- [x] Блоки читаются в порядке position.
- [x] Legacy-контент доступен при отсутствии опубликованных блоков.
- [x] Все текущие 28 уроков открываются.
- [x] Права trainer и существующий прогресс не ослаблены.
- [x] Миграция проверена и применена.
- [x] Тесты и негативные сценарии пройдены.
- [x] Проверен запуск на работающем приложении.

## Риски и ограничения

- Создание и редактирование блоков через admin/API отложено до Iteration 12; сейчас блоки создаются программно или миграцией.
- Автоматический импорт 28 legacy-уроков не выполнялся намеренно: сначала требуется согласовать mapping этапов и политику публикации.
- Code execution, quiz, video, interactive и flashcards пока только зарезервированы как будущие типы; их payload не исполняется.

## Решение о переходе

GO — Iteration 01 завершена.  
Следующий рекомендуемый этап: Iteration 02 — renderer/layout блоков в learning workspace, после согласования импорта первого содержательного урока.
