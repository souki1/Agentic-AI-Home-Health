import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine which .env file to load based on environment
# Priority: .env.local (local dev) > .env (fallback) > .env.production (reference)
_backend_dir = Path(__file__).resolve().parent
_env_local = _backend_dir / ".env.local"
_env_default = _backend_dir / ".env"
_env_production = _backend_dir / ".env.production"

# For local development, prefer .env.local if it exists
# Otherwise use .env (which can be created from .env.example)
# .env.production is mainly for reference/documentation
if _env_local.exists():
    _env_path = _env_local
elif _env_default.exists():
    _env_path = _env_default
else:
    # Fallback to .env.production if neither exists (for reference)
    _env_path = _env_production if _env_production.exists() else _env_default


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_path,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database connection (from env)
    database_url: str = "postgresql://postgres:root@localhost:5432/health_analytics"
    
    # Cloud SQL (if using Unix socket instead of DATABASE_URL)
    instance_connection_name: str = ""  # e.g. "project:region:instance"
    db_user: str = "postgres"
    db_pass: str = ""  # Set via Secret Manager in production
    db_name: str = "health_analytics"
    
    # Auth
    secret_key: str = "root"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    
    # CORS: comma-separated list of allowed origins (set in env for production)
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"

    # ----- GCP Vertex AI RAG (optional) -----
    google_cloud_project: str = ""
    google_cloud_location: str = "us-central1"
    vertex_embedding_model: str = "text-embedding-005"
    vertex_embedding_dimensions: int = 768
    vertex_rag_llm_model: str = "gemini-1.5-flash-001"
    vector_search_index_id: str = ""
    vector_search_index_endpoint_id: str = ""
    vector_search_top_k: int = 10
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 50
    # Path to JSON file with {"chunk_id": "text"} for lookup (optional; can use in-memory store)
    rag_chunk_store_path: str = ""


settings = Settings()
