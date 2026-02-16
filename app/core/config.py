from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "SciTinder API"
    app_env: str = Field("dev", alias="APP_ENV")

    # Готовая строка подключения из .env (если есть)
    db_url: str | None = Field(None, alias="DB_URL")

    # Postgres (fallback, если DB_URL не задан)
    pg_host: str = Field("localhost", alias="PG_HOST")
    pg_port: int = Field(5433, alias="PG_PORT")
    pg_db: str = Field("scopus", alias="PG_DB")
    pg_user: str = Field("postgres", alias="PG_USER")
    pg_password: str = Field("root", alias="PG_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # игнорируем лишние переменные окружения
    )

    @property
    def sqlalchemy_database_uri(self) -> str:
        """
        Строка подключения для sync-SQLAlchemy:
        - если есть DB_URL с asyncpg, заменяем драйвер на psycopg2
        - иначе собираем из PG_*
        """
        if self.db_url:
            return self.db_url.replace("postgresql+asyncpg", "postgresql+psycopg2")

        return (
            f"postgresql+psycopg2://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )

    @property
    def sqlalchemy_async_database_uri(self) -> str:
        """
        Строка подключения для async-SQLAlchemy.
        Если DB_URL уже задан и содержит asyncpg — используем его как есть.
        Иначе собираем URL с драйвером asyncpg.
        """
        if self.db_url:
            if "asyncpg" in self.db_url:
                return self.db_url
            return self.db_url.replace("postgresql+psycopg2", "postgresql+asyncpg")

        return (
            f"postgresql+asyncpg://{self.pg_user}:{self.pg_password}"
            f"@{self.pg_host}:{self.pg_port}/{self.pg_db}"
        )


settings = Settings()

