# The personal web-site by backend-developer [![Python Version](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/release/python-3110/) [![Django Version](https://img.shields.io/badge/django-4.2-green)](https://docs.djangoproject.com/en/4.2/) [![Bootstrap Version](https://img.shields.io/badge/bootstrap-5.0-red)](https://getbootstrap.com/docs/4.3/getting-started/introduction/) [![HTML](https://img.shields.io/badge/HTML-5-red)](https://developer.mozilla.org/en-US/docs/Web/Guide/HTML/HTML5) [![CSS](https://img.shields.io/badge/CSS-3-blue)](https://developer.mozilla.org/en-US/docs/Web/CSS) [![PostreSQL](https://img.shields.io/badge/PostreSQL-14.8-blue)](https://developer.mozilla.org/en-US/docs/Web/CSS)


## Description


## Features


## Technologies Used
* Django 4
* Bootstrap 5
* HTML5
* CSS
* PostgreSQL
* SQLite3

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
ALLOWED_HOSTS=127.0.0.1, localhost
EMAIL_HOST_USER='your-email@yandex.ru'
EMAIL_HOST_PASSWORD='your-password'
EMAIL_ADMIN='your-email@yandex.ru'
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
MODE=prod # --> IF NEED `SQLite3` write: dev
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
python manage.py runserver
python manage.py runserver_plus --cert-file cert.crt #SSL
```

8. Open your web browser and navigate to http://localhost:8000 to view the application.


## Credits
This project was created by [Evgeniy Volochek](https://github.com/EvgVol). The Bootstrap framework was used to assist with the layout and styling of the website.

## License
This project is licensed under the MIT License. See the LICENSE.md file for details.