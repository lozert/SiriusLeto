# SciTinder API

API для SciTinder: поиск по авторам и публикациям. FastAPI-приложение с асинхронным подключением к PostgreSQL.

## Требования

- **Python** 3.13+
- **Poetry** (менеджер зависимостей)
- **PostgreSQL** (порт по умолчанию в конфиге: 5433)

## Установка

### 1. Клонирование и переход в каталог проекта

```bash
cd TestConnetion
```

### 2. Установка зависимостей через Poetry

```bash
poetry install
```

Для установки только production-зависимостей (без dev):

```bash
poetry install --only main
```

### 3. Переменные окружения

Создайте файл `.env` в корне проекта (или задайте переменные в системе).

**Вариант 1 — отдельные параметры PostgreSQL:**

```env
PG_HOST=localhost
PG_PORT=5433
PG_DB=scopus
PG_USER=postgres
PG_PASSWORD=root
APP_ENV=dev
```

**Вариант 2 — готовая строка подключения:**

```env
# Для приложения (async)
DB_URL=postgresql+asyncpg://postgres:root@localhost:5433/scopus
APP_ENV=dev
```

Если `.env` не задан, используются значения по умолчанию из `app/core/config.py` (localhost:5433, БД `scopus`, пользователь `postgres`, пароль `root`).

### 4. База данных и миграции

Убедитесь, что PostgreSQL запущен и создана база (например, `scopus`). Затем выполните миграции Alembic:

```bash
poetry run alembic upgrade head
```

Создание новой миграции после изменения моделей:

```bash
poetry run alembic revision --autogenerate -m "описание изменений"
```

### 5. Запуск приложения

**Через Poetry:**

```bash
poetry run python main.py
```

**Или через uvicorn напрямую (из активированного окружения):**

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Сервер будет доступен по адресу: **http://localhost:8000**

- Документация API (Swagger): http://localhost:8000/docs  
- Корневой маршрут: http://localhost:8000/  
- Проверка здоровья: http://localhost:8000/health  

## Структура проекта

- `app/` — код приложения
  - `api/v1/routers/` — маршруты (authors, health, organization_topics, recommendations)
  - `core/` — конфигурация, логирование
  - `db/` — модели SQLAlchemy и сессия БД
  - `repositories/` — слой доступа к данным
  - `schemas/` — Pydantic-схемы
  - `services/` — бизнес-логика
- `alembic/` — миграции БД
- `main.py` — точка входа FastAPI

## Локальный тест без векторной базы (Milvus)

Пока коллекции с эмбеддингами топиков в Milvus не развёрнуты, можно запускать приложение с **поиском топиков по тексту в PostgreSQL** (fallback):

1. В `.env` добавьте или установите:
   ```env
   USE_VECTOR_SEARCH=false
   ```
2. Запустите бэкенд и фронтенд как обычно. Рекомендации будут считаться по топикам, найденным через `ILIKE` по названию в таблице `topic`, далее — те же коэффициенты из `organization_topic`.

Если `USE_VECTOR_SEARCH=true` (по умолчанию), но коллекция в Milvus недоступна или пуста, сервис автоматически переключится на этот же текстовый fallback. Эмбеддер (TorchServe) при fallback не вызывается.

## Разработка

- Линтер и форматирование: `poetry run ruff check .` / `poetry run ruff format .`
- Типы: `poetry run mypy app`
- Тесты: `poetry run pytest`

## Лицензия

Проект в текущем виде без указания лицензии.
