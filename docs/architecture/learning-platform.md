# Архитектура образовательной платформы Read More: аудит baseline

Дата аудита: 2026-10-12  
Пилот: курс «ML-инженер»  
Репозиторий: /Users/volochek_es/Documents/DEV/read-more

## Фактический стек

- Python 3.11, Django 4.2.4, Django REST Framework 3.14.
- ASGI-сервер Daphne 4.0.0; ASGI_APPLICATION настроен на website.asgi.application.
- PostgreSQL 13 Alpine в Docker Compose; движок и параметры берутся из .env.
- Redis 7.0.4 используется для cache и Channels; Redis DB 1/2 задействованы Celery broker/result backend.
- Celery 5.3.1 присутствует в зависимостях и описан сервисом celery_worker, но во время аудита worker не был запущен.
- Nginx 1.21.3 Alpine отдаёт /static/ и /media/, проксирует приложение и поддерживает WebSocket-маршрут /ws/.
- Интерфейс — Django templates, Bootstrap/существующая CSS/JS-стилизация; отдельного React/Vue frontend и сборщика не обнаружено.
- Markdown рендерится на сервере библиотекой Markdown 3.4.4 через courses.services.lesson_document.

## Существующие сущности

### Каталог и содержание

- Course — владелец, направление, описание, сложность, нагрузка, изображения, студенты и slug.
- Module — курс, название, описание и порядок.
- Lesson — модуль, название и порядок.
- Content плюс generic-представления Text, Image, Video, File — старый контентный слой, привязанный к модулю, а не к уроку.
- LessonMaterial — OneToOne к уроку; текстовые поля objectives, theory, practice, self_check, resources.
- LessonProgress — пользователь, урок, status, current_step, временные метки; уникальность user/lesson.
- LessonProgressEvent — журнал событий по прогрессу.

### Чего сейчас нет

Не обнаружены отдельные модели или контракты для LessonBlock, версий блоков, Assessment/Question/AnswerAttempt, CodeSubmission/Code Runner, ReviewItem/ReviewAttempt, TutorConversation и Mastery Score. Поэтому Iteration 01 должна расширять текущую модель постепенно и не удалять LessonMaterial.

## Маршруты

- /ru/courses/ — каталог курсов.
- /ru/course/<slug>/trainer/ — рабочая область курса.
- /ru/course/<slug>/trainer/<module_id>/ — рабочая область модуля.
- /ru/course/<slug>/trainer/<module_id>/lesson/<lesson_id>/ — урок с пятью этапами.
- /ru/course/<slug>/trainer/<module_id>/lesson/<lesson_id>/progress/ — POST сохранения этапа.
- /ru/api/courses/ — read-only DRF ViewSet.
- /ru/api/courses/<id>/enroll/ и /contents/ — API-операции с BasicAuthentication и permission checks.

Trainer защищён авторизацией и доступом владельца/ученика курса. Теория проходит через безопасный серверный renderer с оглавлением, callout-блоками, локальными изображениями и фильтрацией опасных HTML/ссылок.

## Docker и данные

docker-compose.yaml определяет db, cache, web, celery_worker, nginx и certbot. Команда web при старте выполняет миграции, seed_ml_course, seed_ml_materials, затем запускает Daphne. Статика копируется в named volume static_value, media — в media_value.

seed_ml_course пересоздаёт модули и уроки курса, поэтому его нельзя считать безопасным для пользовательского прогресса: перед изменением seed-политики Iteration 01 требуется отдельный тест сохранности LessonProgress. seed_ml_materials использует update_or_create по уроку и не создаёт дубликаты материалов.

## Карта зависимостей

Browser → Nginx → Daphne/Django

  Course → Module → Lesson
                      ├── LessonMaterial, legacy structured text
                      ├── LessonProgress → LessonProgressEvent
                      └── future LessonBlock(s)

  Django → PostgreSQL
         → Redis / Channels
         → Celery, configured but not active in audit

## Риски

1. LessonMaterial хранит весь урок в пяти больших текстовых полях; переход к блокам требует обратимого legacy-адаптера.
2. Seed курса удаляет и создаёт модули/уроки заново; возможна потеря внешних связей и прогресса при изменении каталога.
3. Текущий API курса не является API интерактивных блоков и использует BasicAuthentication для части операций.
4. Без отдельного изолированного Code Runner нельзя выполнять пользовательский Python в Django/Daphne.
5. Без версионирования блока изменение опубликованного текста может сделать старые попытки и прогресс неоднозначными.
6. Markdown уже имеет безопасный renderer, но новый block payload потребует отдельной серверной валидации по типу и версии схемы.
7. Celery описан в Compose, но worker не был запущен в baseline; фоновые сценарии нельзя считать проверенными.
8. Nginx и Django используют отдельные static/media volume; после добавления ассетов необходим HTTP smoke-check через Nginx.

## Решение для Iteration 01

Добавлять LessonBlock как новую сущность, сохранив LessonMaterial и текущий trainer. Начальная миграция должна быть обратимой: legacy-материал читается как виртуальный набор блоков или импортируется с явной меткой источника. Публикация, версии и admin UI не должны появляться частично: сначала модель, validation и read-layer, затем renderer.
