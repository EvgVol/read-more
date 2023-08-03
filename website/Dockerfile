FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "website.wsgi:application", "--bind", "0:8000" ]
