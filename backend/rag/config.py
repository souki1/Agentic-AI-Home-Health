"""RAG config from app settings."""
from config import settings

GOOGLE_CLOUD_PROJECT = settings.google_cloud_project or ""
GOOGLE_CLOUD_LOCATION = settings.google_cloud_location or "us-central1"
EMBEDDING_MODEL = settings.vertex_embedding_model or "text-embedding-005"
EMBEDDING_DIMENSIONS = settings.vertex_embedding_dimensions or 768
RAG_LLM_MODEL = settings.vertex_rag_llm_model or "gemini-1.5-flash-001"
VECTOR_SEARCH_INDEX_ID = settings.vector_search_index_id or ""
VECTOR_SEARCH_INDEX_ENDPOINT_ID = settings.vector_search_index_endpoint_id or ""
VECTOR_SEARCH_TOP_K = settings.vector_search_top_k or 10
CHUNK_SIZE = settings.rag_chunk_size or 512
CHUNK_OVERLAP = settings.rag_chunk_overlap or 50
