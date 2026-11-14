
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Palm Mind Intelligent Document Assistant"

    database_url: str
    redis_url: str
    qdrant_url: str

    qdrant_api_key: SecretStr | None = None
    qdrant_collection: str = "document_chunks"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    groq_api_key: SecretStr = SecretStr("")
    groq_model: str = "openai/gpt-oss-20b"

    max_upload_size_mb: int = 20
    upload_dir: Path = Path("uploads")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
