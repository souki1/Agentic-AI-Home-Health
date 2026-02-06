"""Load from .env in backend folder."""
import os

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


def _resolve_database_url(value: str) -> str:
    """If value is a path to a file (e.g. Cloud Run secret mount), read the file content."""
    if not value or not value.strip():
        return value
    s = value.strip()
    if s.startswith("/") and os.path.isfile(s):
        with open(s, "r") as f:
            return f.read().strip()
    return s


class Settings(BaseSettings):
    database_url: str = Field(default="", description="PostgreSQL URL (required for DB; empty allows server to start for Cloud Run health checks)")
    secret_key: str = Field(default="change-me-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=10080, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    cors_origins: str = Field(default="http://localhost:5173,http://127.0.0.1:5173", env="CORS_ORIGINS")
    
    # LLM / RAG settings
    llm_provider: str = Field(default="ollama", env="LLM_PROVIDER", description="'ollama' for local, 'vertex' for cloud")
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.2", env="OLLAMA_MODEL")
    google_cloud_project: str = Field(default="", env="GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = Field(default="us-central1", env="GOOGLE_CLOUD_LOCATION")
    vertex_model: str = Field(default="gemini-2.0-flash-001", env="VERTEX_MODEL")
    vector_search_index_endpoint_id: str = Field(default="", env="VECTOR_SEARCH_INDEX_ENDPOINT_ID")

    model_config = {"env_file": (".env", ".env.local", ".env.production"), "extra": "ignore"}

    @model_validator(mode="after")
    def resolve_secret_paths(self):
        self.database_url = _resolve_database_url(self.database_url)
        # Fallback: Cloud Run / GitHub may set GCP_PROJECT_ID instead of GOOGLE_CLOUD_PROJECT
        if not (self.google_cloud_project or "").strip():
            fallback = (os.environ.get("GCP_PROJECT_ID") or "").strip()
            if fallback:
                self.google_cloud_project = fallback
        return self

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
