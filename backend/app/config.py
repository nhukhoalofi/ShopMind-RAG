from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "ShopMind RAG API"
    app_env: str = "development"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "shopmind_chunks"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    groq_api_key: str | None = Field(default=None, repr=False)
    groq_model: str = "llama-3.3-70b-versatile"
    top_k: int = Field(default=5, ge=1)
    min_score: float = Field(default=0.68, ge=-1.0, le=1.0)
    max_score_gap: float = Field(default=0.12, ge=0.0)
    max_context_chars: int = Field(default=4500, ge=1)
    llm_temperature: float = Field(default=0.1, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=500, ge=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
