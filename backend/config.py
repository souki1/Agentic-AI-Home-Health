import os
import logging
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Detect if we're running in Cloud Run or production environment
# Cloud Run sets K_SERVICE and K_REVISION env vars
_is_cloud_run = bool(os.getenv("K_SERVICE") or os.getenv("K_REVISION"))
_is_production = _is_cloud_run or os.getenv("ENVIRONMENT") == "production"

# Determine which .env file to load (only for local development)
# In Cloud Run/production, environment variables come from Cloud Run env vars/secrets, not .env files
_backend_dir = Path(__file__).resolve().parent
_env_local = _backend_dir / ".env.local"
_env_default = _backend_dir / ".env"

# Only load .env files for local development
# In production (Cloud Run), pydantic-settings reads directly from os.environ
if _is_production:
    # Production: Don't load .env files, use environment variables from Cloud Run
    _env_path = None
    logger.info(f"Running in production (Cloud Run: {_is_cloud_run}). Using environment variables from Cloud Run, not .env files.")
elif _env_local.exists():
    # Local dev: prefer .env.local
    _env_path = _env_local
    logger.debug(f"Loading environment from .env.local")
elif _env_default.exists():
    # Local dev: fallback to .env
    _env_path = _env_default
    logger.debug(f"Loading environment from .env")
else:
    # No .env files found - will use defaults and environment variables
    _env_path = None
    logger.debug("No .env files found. Using defaults and environment variables.")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_path,  # None in production, .env.local or .env in dev
        env_file_encoding="utf-8" if _env_path else None,
        extra="ignore",
        # In production, read from environment variables (Cloud Run sets these)
        # In dev, read from .env file AND environment variables (env vars override .env)
    )

    # ============================================================================
    # Database Configuration
    # ============================================================================
    # ALL values MUST come from environment variables (.env.local or Cloud Run env vars)
    # NO hardcoded defaults - everything read from env files
    
    # Option A: Direct connection string (DATABASE_URL env var)
    database_url: Optional[str] = None
    
    # Option B: Cloud SQL via Unix socket (if INSTANCE_CONNECTION_NAME is set)
    instance_connection_name: Optional[str] = None  # INSTANCE_CONNECTION_NAME env var
    db_user: Optional[str] = None  # DB_USER env var
    db_pass: Optional[str] = None  # DB_PASS env var (from Secret Manager in production)
    db_name: Optional[str] = None  # DB_NAME env var
    db_host: Optional[str] = None  # DB_HOST env var
    db_port: Optional[int] = None  # DB_PORT env var
    db_sslmode: Optional[str] = None  # DB_SSLMODE env var
    
    # ============================================================================
    # Authentication Configuration
    # ============================================================================
    # ALL values MUST come from environment variables
    secret_key: Optional[str] = None  # SECRET_KEY env var (REQUIRED)
    algorithm: Optional[str] = None  # ALGORITHM env var
    access_token_expire_minutes: Optional[int] = None  # ACCESS_TOKEN_EXPIRE_MINUTES env var
    
    # ============================================================================
    # CORS Configuration
    # ============================================================================
    cors_origins: Optional[str] = None  # CORS_ORIGINS env var (REQUIRED)
    
    # ============================================================================
    # GCP Vertex AI RAG Configuration (optional)
    # ============================================================================
    # ALL values MUST come from environment variables
    google_cloud_project: Optional[str] = None  # GOOGLE_CLOUD_PROJECT env var
    google_cloud_location: Optional[str] = None  # GOOGLE_CLOUD_LOCATION env var
    vertex_embedding_model: Optional[str] = None  # VERTEX_EMBEDDING_MODEL env var
    vertex_embedding_dimensions: Optional[int] = None  # VERTEX_EMBEDDING_DIMENSIONS env var
    vertex_rag_llm_model: Optional[str] = None  # VERTEX_RAG_LLM_MODEL env var
    vector_search_index_id: Optional[str] = None  # VECTOR_SEARCH_INDEX_ID env var
    vector_search_index_endpoint_id: Optional[str] = None  # VECTOR_SEARCH_INDEX_ENDPOINT_ID env var
    vector_search_top_k: Optional[int] = None  # VECTOR_SEARCH_TOP_K env var
    rag_chunk_size: Optional[int] = None  # RAG_CHUNK_SIZE env var
    rag_chunk_overlap: Optional[int] = None  # RAG_CHUNK_OVERLAP env var
    rag_chunk_store_path: Optional[str] = None  # RAG_CHUNK_STORE_PATH env var


# Create settings instance
settings = Settings()

# Validate required settings after loading
def validate_settings():
    """Validate that required settings are present from environment variables."""
    errors = []
    
    # Database validation - must come from env vars
    if not settings.instance_connection_name and not settings.database_url:
        errors.append("Either DATABASE_URL or INSTANCE_CONNECTION_NAME must be set in environment variables")
    
    if settings.instance_connection_name:
        # Cloud SQL requires these fields from env vars
        if not settings.db_user:
            errors.append("DB_USER must be set in environment variables when using INSTANCE_CONNECTION_NAME")
        if not settings.db_name:
            errors.append("DB_NAME must be set in environment variables when using INSTANCE_CONNECTION_NAME")
        if settings.db_port is None:
            errors.append("DB_PORT must be set in environment variables (e.g., DB_PORT=5432)")
        if not settings.db_sslmode:
            errors.append("DB_SSLMODE must be set in environment variables (e.g., DB_SSLMODE=require)")
    
    # Auth validation - must come from env vars
    if not settings.secret_key:
        errors.append("SECRET_KEY must be set in environment variables")
    if not settings.algorithm:
        errors.append("ALGORITHM must be set in environment variables (e.g., ALGORITHM=HS256)")
    if settings.access_token_expire_minutes is None:
        errors.append("ACCESS_TOKEN_EXPIRE_MINUTES must be set in environment variables (e.g., ACCESS_TOKEN_EXPIRE_MINUTES=10080)")
    
    # CORS validation - must come from env vars
    if not settings.cors_origins:
        errors.append("CORS_ORIGINS must be set in environment variables")
    
    if errors:
        env_file_hint = f"Check your {_env_path.name} file" if _env_path else "Check your Cloud Run environment variables"
        error_msg = "Missing required environment variables (all values must come from env files, not hardcoded):\n" + "\n".join(f"  - {e}" for e in errors) + f"\n\n{env_file_hint}"
        if _is_production:
            logger.error(error_msg)
            raise ValueError(error_msg)
        else:
            logger.warning(error_msg)
            logger.warning("Some features may not work correctly. All values must be set in .env.local file.")


# Validate settings on import (only warn in dev, error in production)
try:
    validate_settings()
except ValueError:
    # Re-raise in production
    if _is_production:
        raise
