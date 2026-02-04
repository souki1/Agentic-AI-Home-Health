"""
Vertex AI Embeddings: index documents (RETRIEVAL_DOCUMENT) and embed queries (RETRIEVAL_QUERY).
"""
from __future__ import annotations

from typing import List

from rag.config import (
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
    GOOGLE_CLOUD_LOCATION,
    GOOGLE_CLOUD_PROJECT,
)
from rag.chunking import Chunk


def _get_client():
    import os
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
    if GOOGLE_CLOUD_PROJECT:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", GOOGLE_CLOUD_PROJECT)
    if GOOGLE_CLOUD_LOCATION:
        os.environ.setdefault("GOOGLE_CLOUD_LOCATION", GOOGLE_CLOUD_LOCATION)
    from google import genai
    return genai.Client(
        vertexai=True,
        project=GOOGLE_CLOUD_PROJECT,
        location=GOOGLE_CLOUD_LOCATION,
    )


def embed_documents(texts: List[str], title: str | None = None) -> List[List[float]]:
    """Embed document chunks for indexing (RETRIEVAL_DOCUMENT)."""
    if not texts:
        return []
    client = _get_client()
    config = {"task_type": "RETRIEVAL_DOCUMENT", "output_dimensionality": EMBEDDING_DIMENSIONS}
    if title:
        config["title"] = title
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=config,
    )
    return [e.values for e in response.embeddings]


def embed_query(query: str) -> List[float]:
    """Embed a single query for retrieval (RETRIEVAL_QUERY)."""
    client = _get_client()
    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=[query],
        config={"task_type": "RETRIEVAL_QUERY", "output_dimensionality": EMBEDDING_DIMENSIONS},
    )
    return response.embeddings[0].values


def chunks_to_embeddings(
    chunks: List[Chunk], batch_size: int = 100
) -> List[tuple[str, List[float]]]:
    """Embed chunks in batches; returns (chunk_id, vector)."""
    out: List[tuple[str, List[float]]] = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c.text for c in batch]
        vectors = embed_documents(texts)
        for ch, vec in zip(batch, vectors):
            out.append((ch.id, vec))
    return out
