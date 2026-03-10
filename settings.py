# src/app/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    milvus_host: str = Field("localhost", alias="MILVUS_HOST")
    milvus_port: int = Field(19530, alias="MILVUS_PORT")
    milvus_dim: int = Field(1024, alias="MILVUS_DIM")
    milvus_topic_collection: str = Field("Topic", alias="MILVUS_TOPIC")

    embedding_model_name_or_path: str = Field(
        "multilingual-e5-large",
        alias="EMBEDDING_MODEL_NAME_OR_PATH",
    )
    embedding_device: str = Field("cpu", alias="EMBEDDING_DEVICE")
    embedding_batch_size: int = Field(16, alias="EMBEDDING_BATCH_SIZE")

    vectorize_url: str = Field(
        "https://sci-tinder-stage.lab.pish.pstu.ru/fastapi/vectorize",
        alias="VECTORIZER_URL",
    )

    app_log_level: str = Field("INFO", alias="APP_LOG_LEVEL")
    app_env: str = Field("dev", alias="APP_ENV")
    app_remote_status: str = Field("localhost", alias="APP_REMOTE_STATUS")
    use_vector_search: bool = Field(True, alias="USE_VECTOR_SEARCH")

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def milvus_url(self) -> str:
        if self.app_remote_status == "localhost":
            return f"http://{self.milvus_host}:{self.milvus_port}"
        if self.app_remote_status == "nginx":
            return f"https://{self.milvus_host}/fastapi"
        return f"http://{self.milvus_host}:{self.milvus_port}"

settings = Settings()
