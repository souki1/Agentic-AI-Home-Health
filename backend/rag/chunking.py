"""
Chunking for RAG: produce chunks with id, text, metadata for embedding and indexing.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import List


@dataclass
class Chunk:
    id: str
    text: str
    metadata: dict


def _make_id(text: str, source: str, index: int) -> str:
    raw = f"{source}:{index}:{text[:200]}"
    return hashlib.sha256(raw.encode()).hexdigest()[:24]


def chunk_by_fixed_size(
    text: str,
    source_id: str = "doc",
    chunk_size: int = 512,
    chunk_overlap: int = 50,
    sep: str = "\n",
) -> List[Chunk]:
    """Split text into overlapping chunks; respect separator when possible."""
    if not text.strip():
        return []
    chunks: List[Chunk] = []
    current: List[str] = []
    current_len = 0
    index = 0
    parts = text.split(sep) if sep else [text]
    for part in parts:
        part_len = len(part) + (len(sep) if current else 0)
        if current_len + part_len > chunk_size and current:
            text_chunk = sep.join(current)
            chunks.append(
                Chunk(
                    id=_make_id(text_chunk, source_id, index),
                    text=text_chunk,
                    metadata={"source": source_id, "chunk_index": index},
                )
            )
            index += 1
            if chunk_overlap > 0 and current:
                overlap_text = sep.join(current)
                overlap_len = min(chunk_overlap, len(overlap_text))
                overlap_start = len(overlap_text) - overlap_len
                current = [overlap_text[overlap_start:]] if overlap_len else []
                current_len = sum(len(p) for p in current)
            else:
                current = []
                current_len = 0
        current.append(part)
        current_len += part_len
    if current:
        text_chunk = sep.join(current)
        chunks.append(
            Chunk(
                id=_make_id(text_chunk, source_id, index),
                text=text_chunk,
                metadata={"source": source_id, "chunk_index": index},
            )
        )
    return chunks


def chunk_by_sentences(
    text: str,
    source_id: str = "doc",
    max_sentences: int = 5,
    chunk_overlap_sentences: int = 1,
) -> List[Chunk]:
    """Split by sentences, then group into chunks with overlap."""
    sentence_end = re.compile(r"(?<=[.!?])\s+")
    sentences = [s.strip() for s in sentence_end.split(text) if s.strip()]
    if not sentences:
        return []
    chunks: List[Chunk] = []
    start = 0
    index = 0
    while start < len(sentences):
        end = min(start + max_sentences, len(sentences))
        group = sentences[start:end]
        text_chunk = " ".join(group)
        chunks.append(
            Chunk(
                id=_make_id(text_chunk, source_id, index),
                text=text_chunk,
                metadata={"source": source_id, "chunk_index": index},
            )
        )
        index += 1
        start = end - chunk_overlap_sentences if chunk_overlap_sentences > 0 else end
    return chunks
