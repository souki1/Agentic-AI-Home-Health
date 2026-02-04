"""
Vertex AI Vector Search: query a deployed index endpoint for nearest neighbors.
"""
from __future__ import annotations

from typing import List

from rag.config import (
    GOOGLE_CLOUD_LOCATION,
    GOOGLE_CLOUD_PROJECT,
    VECTOR_SEARCH_INDEX_ENDPOINT_ID,
    VECTOR_SEARCH_INDEX_ID,
    VECTOR_SEARCH_TOP_K,
)

DEPLOYED_INDEX_ID = "default"


def find_neighbors(
    query_embedding: List[float],
    top_k: int | None = None,
    deployed_index_id: str | None = None,
) -> List[dict]:
    """Query the deployed Vector Search index. Returns list of dicts with 'id' and 'distance'."""
    top_k = top_k or VECTOR_SEARCH_TOP_K
    if not GOOGLE_CLOUD_PROJECT or not VECTOR_SEARCH_INDEX_ENDPOINT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT and VECTOR_SEARCH_INDEX_ENDPOINT_ID must be set")

    from google.cloud import aiplatform

    aiplatform.init(project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION)
    endpoint = aiplatform.MatchingEngineIndexEndpoint(VECTOR_SEARCH_INDEX_ENDPOINT_ID)
    did = deployed_index_id or DEPLOYED_INDEX_ID
    responses = endpoint.find_neighbors(
        deployed_index_id=did,
        queries=[query_embedding],
        num_neighbors=top_k,
    )
    results: List[dict] = []
    if responses and responses[0]:
        for neighbor in responses[0]:
            results.append({
                "id": getattr(neighbor, "id", None) or getattr(
                    getattr(neighbor, "datapoint", None), "datapoint_id", None
                ),
                "distance": getattr(neighbor, "distance", None),
            })
    return results
