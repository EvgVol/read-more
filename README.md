# READ MORE - service for training
[![Certbot](https://img.shields.io/badge/-Certbot-003A6E?style=flat&logo=letsencrypt&logoColor=white)](https://certbot.eff.org/)
[![READ MORE workflow](https://github.com/EvgVol/read-more/actions/workflows/main.yml/badge.svg)](https://github.com/EvgVol/read-more/actions/workflows/main.yml)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/release/python-3110/)
[![JavaScript](https://img.shields.io/badge/JavaScript-yellow)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Django](https://img.shields.io/badge/django-4.2-green)](https://docs.djangoproject.com/en/4.2/)
[![Django Rest Framework](https://img.shields.io/badge/Django%20Rest%20Framework-v3.12-green)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![Docker Compose](https://img.shields.io/badge/-Docker_Compose-384d54?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Redis](https://img.shields.io/badge/Redis-red)](https://redis.io/documentation)
[![Memcached](https://img.shields.io/badge/Memcached-red)](https://memcached.org/documentation)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-red)](https://www.rabbitmq.com/documentation.html)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13.0-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
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
   - Diverse Course Offerings: We offer a wide range of courses covering various knowledge domains, ranging from programming to arts and sciences.
   - Interactive Learning Materials: Our courses include interactive educational materials, tasks, and projects to make learning engaging and effective.
   - Community: Students can join discussions, ask questions, and share their experiences in our chat and forum.

### Blog - Articles and Discussions: Our blog features articles authored by experts in various fields and allows users to share their knowledge and opinions.
   - Feedback: Readers can comment on articles and participate in discussions, creating an active community.

### Bookstore - Extensive Selection: We provide a catalog of books on various topics to deepen knowledge.
   - Online Purchase: Users can easily purchase books through our interface.

### Student Chat - Online Communication: We provide a platform for students to communicate, ask questions, and support each other during the learning process.



## Technologies Used
* Python 3.11
* JavaScript
* Django 4.2
* Django REST Framework
* Django Channels
* Djang Debug Toolbar 
* PostgreSQL 13+
* SQLite3
* Docker
* Docker Compose
* Redis
* RabbitMQ
* Memcached
* Celery
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
git clone https://github.com/evgvol/read_more.git
```
2. Create a .env file in the root directory of the project.

3. Add the following environment variables to the .env file:
```
SECRET_KEY='django-insecure-51ydgsn!flww^)=p+m5rkp=bpan@q*em8#u^40s^4ug94l6_j('
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
YANDEX_KEY='yandex-key'
YANDEX_SECRET='yandex-secret'
GOOGLE_KEY='google-key'
GOOGLE_SECRET='google-secret'
VK_KEY='vk-key'
VK_SECRET='vk-secret'
SOCIAL_AUTH_GITHUB_KEY='github-key'
SOCIAL_AUTH_GITHUB_SECRET='github-secret'
```

4. Navigate to the project directory using:
```
cd backend
```

5. Install the dependencies using the following command: 
```
pip install -r requirements.txt
```

6.  Start the Redis using the following command:
```
docker pull redis
docker run -it --rm --name redis -p 6379:6379 redis
```

7. Start the Django development server using the following command:
```
python manage.py runserver --settings=website.settings.local

#If you need a SSL using the command below:
python manage.py runserver_plus --cert-file cert.crt
```

8. Open your web browser and navigate to http://localhost:8000 to view the application.


9. To add translations of your source code, use the following command:
```
python manage.py makemessages --all
```
10. Edit `django.po` files in the locale folder of each application using a text editor. After that, run the following command to compile translations:
```
python manage.py compilemessages
```

## SERVER SETUP

1. Connect to your server via SSH, if you haven't already done so, and update the APT package index:

```bash
sudo apt update
```

2. Now update the packages installed in the system and install security updates:

```bash
sudo apt upgrade -y
```

3. Install the Russian localization using the built-in dpkg-reconfigure utility

```bash
sudo dpkg-reconfigure locales 
```

4. Restart the server:

```bash
sudo reboot
```

5. Next, install the necessary PostgreSQL packages:

```bash
sudo apt install postgresql postgresql-contrib -y
```

6. You can manage the database server using standard systemd commands:

```bash
sudo systemctl stop postgresql # Stop 
sudo systemctl start postgresql # Start
sudo systemctl restart postgresql # Restart
sudo systemctl status postgresql # Find out status, current status
```

7. On the command line, on behalf of the postgres user, call the psql utility, this is a client program for connecting and managing a DBMS:

```bash
sudo -u postgres psql
```

8. Now, through psql, create a db_name database:

```bash
CREATE DATABASE db_name;
# Upon successful creation, CREATE DATABASE will return
```

9. Create a user registration record on the database server, then inform Django about this user's data (his username and password). As a result, Django will get access to the database under this name:

```bash
# Сreate a db_user user and come up with your password, more complicated than in the example
CREATE USER db_user WITH ENCRYPTED PASSWORD 'xxxyyyzzz'; 
# give the db_user user all rights when working with the db_name database
GRANT ALL PRIVILEGES ON DATABASE db_name TO db_user;  
```

10. Configure access to PostgreSQL:

Make sure that PostgreSQL allows remote connection if necessary. Edit the pg_hba.conf file, which is located in /etc/postgresql/14/main/pg_hba.conf to allow remote connections if they are required.

11. Configure PostgreSQL settings:

Change the PostgreSQL settings in the postgresql.conf file, which is located in /etc/postgresql/version/main/postgresql.conf. Some parameters that you may need to configure include listen_addresses, max_connections, and others depending on your needs.

12. After making changes, restart PostgreSQL:

```bash
sudo systemctl restart postgresql
```

13. Install Redis:

You can install Redis on Ubuntu using the apt package manager:

```bash
sudo apt install redis-server
```

14. After the installation is complete, start the Redis service and enable it to start on boot:

```bash
udo systemctl start redis-server
sudo systemctl enable redis-server
```

15. Configure Redis (Optional):

By default, Redis is configured to bind to localhost. If you want to allow external connections or make other configuration changes, you can edit the Redis configuration file at /etc/redis/redis.conf.

```bash
bind 0.0.0.0
```

16. Make sure that Redis is really running on the server. You can use the following command to check:

```bash
redis-cli -h 001.222.333.444 -p 6379 ping
#  If the connection is successful, PONG will return
```


## Credits
This project was created by [Evgeniy Volochek](https://github.com/EvgVol). The Bootstrap framework was used to assist with the layout and styling of the website.

## License
This project is licensed under the MIT License. See the LICENSE.md file for details.

## Contributing
If you have any questions, suggestions, requests, or comments, please feel free to open [issues or pull requests](https://github.com/EvgVol/read-more/issues) in this repository.

