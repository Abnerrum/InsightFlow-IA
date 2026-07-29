from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "InsightFlow IA"
    database_url: str = "mysql+pymysql://root:senha@localhost:3306/insightflow_ia"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5"
    obsidian_vault_path: str = str(BASE_DIR / "obsidian-vault")

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
