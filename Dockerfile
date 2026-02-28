# Бэкенд SciTinder API (FastAPI)
FROM python:3.13-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
ENV POETRY_VERSION=1.8.3
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"
ENV POETRY_VIRTUALENVS_CREATE=false

# Зависимости проекта
COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-dev --no-root

# pymilvus (используется в MilvusClient, не в pyproject)
RUN pip install --no-cache-dir pymilvus

# Код приложения
COPY app ./app
COPY main.py settings.py MilvusClient.py ./
COPY alembic.ini ./
COPY alembic ./alembic

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
