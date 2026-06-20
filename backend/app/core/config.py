"""Centralized application configuration (environment-driven, no secrets in code)."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Application
    app_name: str = "SolarOps AI"
    app_env: str = "development"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Wiring
    backend_url: str = "http://localhost:8000"

    # External data sources
    open_meteo_base_url: str = "https://api.open-meteo.com/v1/forecast"
    nasa_power_base_url: str = "https://power.larc.nasa.gov/api/temporal/daily/point"
    weather_use_mock: bool = True

    # LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llm_use_mock: bool = True

    # ML
    model_dir: str = "data/processed/models"
    anomaly_threshold: float = 0.6

    # RAG
    rag_docs_dir: str = "rag/data/manuals"
    rag_index_dir: str = "data/processed/rag_index"
    rag_top_k: int = 4

    @property
    def llm_enabled(self) -> bool:
        """True only when a real LLM should be used."""
        return bool(self.openai_api_key) and not self.llm_use_mock


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
