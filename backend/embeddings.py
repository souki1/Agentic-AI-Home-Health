"""Text embeddings for chat vector search. Uses Vertex AI when LLM provider is vertex."""
from typing import List, Optional

from config import settings


def get_embedding(text: str) -> Optional[List[float]]:
    """
    Return embedding vector for text, or None if embeddings are not available
    (e.g. Ollama provider or Vertex not configured).
    """
    if not text or not text.strip():
        return None
    if settings.llm_provider.lower() != "vertex":
        return None
    if not settings.google_cloud_project:
        return None
    try:
        import vertexai
        from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel

        vertexai.init(project=settings.google_cloud_project, location=settings.google_cloud_location)
        model = TextEmbeddingModel.from_pretrained(settings.vertex_embedding_model)
        # RETRIEVAL_DOCUMENT for stored content; 768 for text-embedding-005
        kwargs = {}
        if settings.vertex_embedding_model.startswith("text-embedding-"):
            kwargs["output_dimensionality"] = 768
        text_input = TextEmbeddingInput(text=text.strip(), task_type="RETRIEVAL_DOCUMENT")
        emb = model.get_embeddings([text_input], **kwargs)
        if emb and len(emb) > 0 and hasattr(emb[0], "values"):
            return list(emb[0].values)
        return None
    except Exception:
        return None
