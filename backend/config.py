"""Load from .env in backend folder."""
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(..., description="PostgreSQL URL (e.g. Cloud SQL or local)")
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=10080, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", env="CORS_ORIGINS")

    model_config = {"env_file": (".env", ".env.local", ".env.production"), "extra": "ignore"}

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
