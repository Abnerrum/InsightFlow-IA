from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "InsightFlow IA"
    app_env: str = "development"
    database_url: str = "mysql+pymysql://root:senha@localhost:3306/insightflow_ia"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5"
    obsidian_vault_path: str = str(BASE_DIR / "obsidian-vault")

    # Segurança e LGPD
    admin_api_key: str | None = None
    data_encryption_key: str | None = None
    audit_hmac_secret: str = "troque-esta-chave-em-producao"
    allowed_origins: str = "http://127.0.0.1:8000,http://localhost:8000"
    rate_limit_per_minute: int = 60
    conversation_retention_days: int = 90
    report_retention_days: int = 365
    privacy_contact_email: str = "privacidade@exemplo.com"

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
