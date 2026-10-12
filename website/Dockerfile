FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y gettext
WORKDIR /code
COPY requirements.txt /code
RUN pip install -r requirements.txt
COPY . .
RUN cp -R /code/static /code/static_source
CMD ["sh", "-c", "cp -R /code/static_source/. /code/static/ && python manage.py migrate --noinput && python manage.py seed_ml_course && python manage.py seed_ml_materials && python manage.py seed_ml_lesson_blocks && python manage.py seed_ml_python_lesson_blocks && python manage.py seed_ml_quiz && python manage.py seed_ml_lesson_2717 && python manage.py audit_ml_learning_content && exec daphne website.asgi:application -b 0.0.0.0 -p 8000"]
