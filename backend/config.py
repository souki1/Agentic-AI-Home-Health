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
