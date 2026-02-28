# src/app/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    milvus_host: str = Field("localhost", alias="MILVUS_HOST")
    milvus_port: int = Field(19530, alias="MILVUS_PORT")
    milvus_dim: int = Field(1024, alias="MILVUS_DIM")

    # TorchServe (e5-large) — задаём частями и собираем URL
    torch_serve_host: str = Field("localhost", alias="TORCH_SERVE_HOST")
    torch_serve_port: int = Field(8081, alias="TORCH_SERVE_PORT")
    torch_serve_predict_endpoint: str = Field("predictions", alias="TORCH_SERVE_PREDICT_ENDPOINT")
    torch_serve_embedder_name: str = Field("e5_large", alias="TORCH_SERVE_EMBEDDER_NAME")

    # App
    app_log_level: str = Field("INFO", alias="APP_LOG_LEVEL")
    app_env: str = Field("dev", alias="APP_ENV")
    app_remote_status: str = Field("localhost", alias="APP_REMOTE_STATUS")
    # Локальный тест без коллекций Milvus: True = векторный поиск, False = поиск топиков по тексту в PostgreSQL
    use_vector_search: bool = Field(True, alias="USE_VECTOR_SEARCH")
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # игнорируем лишние переменные из .env (MILVUS_*, POSTGRES_*, DATABASE_*, DB_URL и т.д.)
    )

    @property
    def milvus_url(self) -> str:
        if self.app_remote_status == "localhost":
            return (f"http://{self.milvus_host}:{self.milvus_port}")
        elif self.app_remote_status == "nginx":
            return (f"https://{self.milvus_host}/fastapi")
    @property
    def torch_serve_url(self) -> str:
        # итог: http://host:port/predictions/e5-large
        if self.app_remote_status == "localhost":
            return (f"http://{self.torch_serve_host}:{self.torch_serve_port}/"
                    f"{self.torch_serve_predict_endpoint}/{self.torch_serve_embedder_name}")
        elif self.app_remote_status == "nginx":
            return (f"https://{self.torch_serve_host}/torch-serve/{self.torch_serve_predict_endpoint}/{self.torch_serve_embedder_name}")
        
settings = Settings()

