from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env from the directory containing this file (backend/)
_env_path = Path(__file__).resolve().parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "postgresql://postgres:root@localhost:5432/health_analytics"
    secret_key: str = "root"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days


settings = Settings()
