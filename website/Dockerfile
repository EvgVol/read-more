FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y gettext
WORKDIR /code
COPY requirements.txt /code
RUN pip install -r requirements.txt
COPY . .
CMD ["daphne", "website.asgi:application", "-b", "0.0.0.0", "-p", "8000"]