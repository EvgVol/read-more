# READ MORE - service for training
[![Certbot](https://img.shields.io/badge/-Certbot-003A6E?style=flat&logo=letsencrypt&logoColor=white)](https://certbot.eff.org/)
[![READ MORE workflow](https://github.com/EvgVol/read-more/actions/workflows/main.yml/badge.svg)](https://github.com/EvgVol/read-more/actions/workflows/main.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/release/python-3110/)
[![JavaScript](https://img.shields.io/badge/JavaScript-yellow)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Django](https://img.shields.io/badge/django-5.2-green)](https://docs.djangoproject.com/en/5.2/)
[![Django Rest Framework](https://img.shields.io/badge/Django%20Rest%20Framework-v3.12-green)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/-Docker_Compose-384d54?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Redis](https://img.shields.io/badge/Redis-red)](https://redis.io/documentation)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Daphne](https://img.shields.io/badge/Daphne-blue)](https://github.com/django/daphne)
[![Celery](https://img.shields.io/badge/Celery-green)](https://docs.celeryproject.org/en/stable/index.html)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-green)](https://docs.gunicorn.org/en/stable/)
[![Daphne](https://img.shields.io/badge/Daphne-blue)](https://github.com/django/daphne)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![Bootstrap Version](https://img.shields.io/badge/bootstrap-5.0-red)](https://getbootstrap.com/docs/4.3/getting-started/introduction/)
[![HTML](https://img.shields.io/badge/HTML-5-red)](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5)
[![CSS](https://img.shields.io/badge/CSS-3-blue)](https://developer.mozilla.org/en-US/docs/Web/CSS)

## Description

The "READ MORE" project is a web platform developed for the purpose of educating and nurturing students in various fields of knowledge. Our mission is to provide high-quality courses that are accessible to all and create an environment where students can learn, communicate, and exchange knowledge. Our website brings together several key functionalities:

## Features

### Courses and Learning
   - Diverse Course Offerings
   - Interactive Learning Materials
   - Community

### Blog - Articles and Discussions
   - Feedback: Readers can comment on articles and participate in discussions, creating an active community.

### Bookstore - Extensive Selection
   - Online Purchase: Users can easily purchase books through our interface.

### Student Chat - Online Communication



## Technologies Used
* Python 3.11
* JavaScript
* Django 5.2
* Django REST Framework
* Django Channels
* Djang Debug Toolbar 
* PostgreSQL 15
* Docker
* Docker Compose
* Redis
* Celery (broker: Redis)
* OAuth2
* Bootstrap 5
* HTML5
* CSS
* GIT
* Nginx
* Gunicorn
* Daphne
* Certbot
* CI/CD


## Installation
To install and run the project locally, follow these steps:

1. Clone the repository using:
```
git clone https://github.com/EvgVol/read-more.git
```
2. Create a .env file in the root directory of the project.

3. Add the following environment variables to the .env file:
```
SECRET_KEY='your-generated-django-secret-key'
DEBUG=False
ALLOWED_HOSTS=127.0.0.1, localhost, web
EMAIL_HOST_USER='your-email@yandex.ru'
EMAIL_HOST_PASSWORD='your-password'
EMAIL_ADMIN='your-email@yandex.ru'
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres 
DB_HOST=db
DB_PORT=5432
REDIS_HOST='127.0.0.1'
REDIS_PORT=6379
CELERY_BROKER_URL=redis://127.0.0.1:6379/1
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/2
YANDEX_KEY='yandex-key'
YANDEX_SECRET='yandex-secret'
GOOGLE_KEY='google-key'
GOOGLE_SECRET='google-secret'
VK_KEY='vk-key'
VK_SECRET='vk-secret'
SOCIAL_AUTH_GITHUB_KEY='github-key'
SOCIAL_AUTH_GITHUB_SECRET='github-secret'
```

4. Install the dependencies using the following command: 
```
pip install -r website/requirements.txt
```

5.  Start all services (PostgreSQL, Redis, web, celery worker, nginx) using:
```
docker compose up -d --build
```
Redis is started together with the other services via Docker Compose.
The Celery worker uses Redis as the message broker
(`CELERY_BROKER_URL=redis://cache:6379/1`).

6. Start the Django development server (from the `website/` directory):
```
python manage.py runserver
```

7. Open your web browser and navigate to http://localhost:8000 to view the application.


8. To add translations of your source code, use the following command:
```
python manage.py makemessages --all
```
9. Edit `django.po` files in the locale folder of each application using a text editor. After that, run the following command to compile translations:
```
python manage.py compilemessages
```

## DEPLOYMENT

The recommended deployment target is a server running Docker + Docker Compose:

1. Clone the repository on the server.
2. Create a `.env` file with the variables from step 3 above
   (use real credentials; in Docker set `DB_HOST=db`, `REDIS_HOST=cache`).
3. Start the stack:
   ```
   docker compose up -d --build
   ```
4. Run migrations (already done in the image entrypoint, rerun if you
   change models manually):
   ```
   docker compose exec web python manage.py migrate --noinput
   ```

For a manual (non-Docker) deployment:

- Install PostgreSQL 14+ (Django 5.2 requires it) and create the
  database/user referenced by `DB_NAME`, `POSTGRES_USER`, `DB_HOST`,
  `DB_PORT` in `.env`.

> **Upgrading from an older PostgreSQL (13 or below)?** PostgreSQL does
> not auto-upgrade across major versions. If the `postgres_data` volume
> already holds a PG13 database, you must migrate it once before the
> web app will start on `postgres:15`:
> ```
> # on the server, before switching the image
> docker compose stop web celery_worker
> docker compose exec db pg_dumpall -U postgres > /tmp/pg13.dump
> docker compose down db          # removes the PG13 container (volume kept)
> # edit compose: image postgres:15-alpine
> docker compose up -d db
> docker compose exec -T db psql -U postgres -d postgres < /tmp/pg13.dump
> docker compose up -d web celery_worker
> ```
> A fresh install (empty `postgres_data` volume) needs none of this.
- Install Redis and make sure `REDIS_HOST`/`REDIS_PORT` point to it
  (it serves the cache, the Channels layer and the Celery broker).
- Install gettext if you need to compile translations.
- Run `pip install -r website/requirements.txt` and
  `python manage.py migrate && python manage.py runserver`
  (or daphne/gunicorn behind nginx for production).


## Credits
This project was created by [Evgeniy Volochek](https://github.com/EvgVol). The Bootstrap framework was used to assist with the layout and styling of the website.

## License
This project is licensed under the MIT License. See the LICENSE.md file for details.

## Contributing
If you have any questions, suggestions, requests, or comments, please feel free to open [issues or pull requests](https://github.com/EvgVol/read-more/issues) in this repository.

