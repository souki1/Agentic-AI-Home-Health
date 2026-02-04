"""
Script to build/update Vertex AI Vector Search index from RAG chunks in database.
Outputs JSONL file for GCS upload, then you create/update the index in Vertex AI console.
Run from backend/ directory: python scripts/build_vector_index.py
Requires: GOOGLE_CLOUD_PROJECT set, database connected, chunks in rag_chunks table.
"""
import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import SessionLocal
from models import RAGChunk
from rag.chunking import Chunk
from rag.embeddings import chunks_to_embeddings
from rag.config import GOOGLE_CLOUD_PROJECT, EMBEDDING_DIMENSIONS

OUTPUT_FILE = "rag_index_embeddings.jsonl"


def build_index_jsonl():
    """Load chunks from DB, embed them, write JSONL for Vector Search index."""
    db = SessionLocal()
    try:
        if not GOOGLE_CLOUD_PROJECT:
            print("Error: GOOGLE_CLOUD_PROJECT not set in .env")
            return

        # Load all chunks from DB
        db_chunks = db.query(RAGChunk).all()
        if not db_chunks:
            print("No chunks found in database. Ingest documents first (scripts/ingest_health_documents.py)")
            return

        print(f"Found {len(db_chunks)} chunks in database")

        # Convert to Chunk objects
        chunks = [
            Chunk(
                id=chunk.id,
                text=chunk.text,
                metadata={
                    "source": chunk.source or "",
                    **(chunk.chunk_metadata or {}),
                },
            )
            for chunk in db_chunks
        ]

        # Embed in batches
        print("Embedding chunks...")
        embeddings = chunks_to_embeddings(chunks, batch_size=100)
        print(f"✓ Embedded {len(embeddings)} chunks")

        # Write JSONL: {"id": "...", "embedding": [float, ...]}
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            for chunk_id, vec in embeddings:
                f.write(json.dumps({"id": chunk_id, "embedding": vec}) + "\n")

        print(f"\n✓ Wrote {len(embeddings)} embeddings to {OUTPUT_FILE}")
        print(f"\nNext steps:")
        print(f"1. Upload {OUTPUT_FILE} to a GCS bucket (gsutil cp {OUTPUT_FILE} gs://your-bucket/rag/)")
        print(f"2. In Vertex AI Console → Vector Search:")
        print(f"   - Create a new index (or update existing)")
        print(f"   - Set dimensions: {EMBEDDING_DIMENSIONS}")
        print(f"   - Set distance: DOT_PRODUCT_DISTANCE")
        print(f"   - Point contentsDeltaUri to: gs://your-bucket/rag/{OUTPUT_FILE}")
        print(f"3. Deploy the index to an endpoint")
        print(f"4. Set VECTOR_SEARCH_INDEX_ENDPOINT_ID in .env")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Building Vector Search index JSONL from database chunks...")
    build_index_jsonl()
