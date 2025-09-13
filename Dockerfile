FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["sh", "-c", "python manage.py makemigrations salaries && python manage.py makemigrations accounts && python manage.py makemigrations tokens &&  python manage.py migrate && python manage.py runserver 0.0.0.0:3000"]
