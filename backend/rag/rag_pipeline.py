"""
RAG query pipeline: embed query → vector search → build prompt → generate with Vertex LLM.
"""
from __future__ import annotations

from typing import Callable

from rag.embeddings import embed_query
from rag.vector_search import find_neighbors
from rag.config import (
    GOOGLE_CLOUD_LOCATION,
    GOOGLE_CLOUD_PROJECT,
    RAG_LLM_MODEL,
    VECTOR_SEARCH_TOP_K,
)

DEFAULT_SYSTEM = (
    "You are a helpful assistant. Answer the question using only the provided context. "
    "If the context does not contain relevant information, say so. Do not invent facts."
)


def retrieve(
    query: str,
    lookup: Callable[[str], str | None],
    top_k: int | None = None,
) -> list[tuple[str, str]]:
    """Embed query, run vector search, resolve chunk text via lookup(id). Returns (chunk_id, text)."""
    vec = embed_query(query)
    neighbors = find_neighbors(vec, top_k=top_k or VECTOR_SEARCH_TOP_K)
    out: list[tuple[str, str]] = []
    for n in neighbors:
        cid = n.get("id") or n.get("datapoint_id")
        if not cid:
            continue
        text = lookup(cid) if callable(lookup) else (lookup.get(cid) if isinstance(lookup, dict) else None)
        if text:
            out.append((str(cid), text))
    return out


def build_prompt(
    query: str,
    context_chunks: list[tuple[str, str]],
    system: str = DEFAULT_SYSTEM,
    context_sep: str = "\n\n---\n\n",
) -> str:
    """Build full prompt with system, context, and question."""
    context_block = context_sep.join(t for _, t in context_chunks)
    return f"{system}\n\n## Context\n{context_block}\n\n## Question\n{query}"


def generate(prompt: str, model: str | None = None) -> str:
    """Call Vertex AI Gemini to generate the answer."""
    model = model or RAG_LLM_MODEL
    try:
        from google import genai
        client = genai.Client(
            vertexai=True,
            project=GOOGLE_CLOUD_PROJECT,
            location=GOOGLE_CLOUD_LOCATION,
        )
        response = client.models.generate_content(model=model, contents=prompt)
        if response and response.candidates:
            return (response.candidates[0].content.parts[0].text or "").strip()
    except Exception as e:
        return f"[Generation error: {e}]"
    return ""


def query(
    question: str,
    lookup: Callable[[str], str | None],
    top_k: int | None = None,
    system: str = DEFAULT_SYSTEM,
) -> tuple[str, list[tuple[str, str]]]:
    """Full RAG: retrieve context, build prompt, generate. Returns (answer, context chunks)."""
    chunks = retrieve(question, lookup, top_k=top_k)
    prompt = build_prompt(question, chunks, system=system)
    answer = generate(prompt)
    return answer, chunks
