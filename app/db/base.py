from sqlalchemy.orm import declarative_base


Base = declarative_base()

# Импорт моделей, чтобы Alembic видел их metadata
from app.db.models import author  # noqa: F401

