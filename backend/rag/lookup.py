"""
Chunk lookup store: database-first with in-memory fallback.
Checks PostgreSQL rag_chunks table first, then in-memory dict, then JSON file.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_chunk_store: Dict[str, str] = {}
_db_session = None  # Set via set_db_session() if DB lookup is available


def set_db_session(session):
    """Set SQLAlchemy session for database lookup (called from main.py)."""
    global _db_session
    _db_session = session


def get_store() -> Dict[str, str]:
    """Return the current in-memory chunk id -> text lookup."""
    return _chunk_store


def set_store(store: Dict[str, str]) -> None:
    """Replace the in-memory chunk store (e.g. after loading from JSON)."""
    global _chunk_store
    _chunk_store = dict(store)


def load_store_from_path(path: str | Path) -> bool:
    """Load chunk store from a JSON file. Expected format: {"chunk_id": "text", ...} or [{"id": "...", "text": "..."}]. Returns True if loaded."""
    global _chunk_store
    p = Path(path)
    if not p.is_file():
        logger.warning("RAG chunk store path is not a file: %s", path)
        return False
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            _chunk_store = {k: v if isinstance(v, str) else str(v) for k, v in data.items()}
        elif isinstance(data, list):
            _chunk_store = {}
            for item in data:
                if isinstance(item, dict):
                    id_ = item.get("id")
                    text = item.get("text")
                    if id_ is not None and text is not None:
                        _chunk_store[str(id_)] = str(text)
        else:
            logger.warning("RAG chunk store JSON must be object or array of {id, text}")
            return False
        logger.info("RAG chunk store loaded: %d chunks from %s", len(_chunk_store), path)
        return True
    except Exception as e:
        logger.exception("Failed to load RAG chunk store from %s: %s", path, e)
        return False


def lookup(chunk_id: str, db_session=None) -> Optional[str]:
    """
    Return chunk text by id. Checks:
    1. Database (rag_chunks table) if db_session is provided
    2. In-memory store (_chunk_store)
    3. Returns None if not found
    """
    # Try database first
    if db_session is not None:
        try:
            from models import RAGChunk
            chunk = db_session.query(RAGChunk).filter(RAGChunk.id == chunk_id).first()
            if chunk:
                return chunk.text
        except Exception as e:
            logger.debug("DB lookup failed for chunk %s: %s", chunk_id, e)
    # Fallback to in-memory
    return _chunk_store.get(chunk_id)
