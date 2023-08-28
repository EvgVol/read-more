FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "website.wsgi:application", "--bind", "0:8000" ]
