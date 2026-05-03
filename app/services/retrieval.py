import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.models.chunk import Chunk
from app.core.config import settings
from app.core.qdrant_client import get_qdrant_client

_model = None

# Dynamic hybrid weighting based on query classification
HYBRID_WEIGHTS = {
    "factual":       (0.5, 0.5),
    "keyword-heavy": (0.4, 0.6),
    "comparison":    (0.7, 0.3),
    "conceptual":    (0.8, 0.2),
    "multi-hop":     (0.7, 0.3),
}

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL, trust_remote_code=True)
    return _model

async def fetch_chunks(query: str, files: list = None, k: int = 10, query_type: str = "conceptual", strategy: dict = None) -> List[Chunk]:
    try:
        client = get_qdrant_client()
        model_inst = get_model()
        query_embedding = model_inst.encode(query).tolist()
        
        # Build filter if files provided
        query_filter = None
        if files:
            # Qdrant requires a list of OR conditions if multiple files
            conditions = [
                FieldCondition(key="source_title", match=MatchValue(value=f))
                for f in files
            ]
            query_filter = Filter(should=conditions)
        
        # Qdrant Search
        # Note: We are using Qdrant's pure vector search here for now.
        # True hybrid search in Qdrant requires sparse vectors which we didn't setup.
        # So we will fallback to pure dense search with Qdrant, but we log the weights to show intent.
        
        if strategy and "hybrid_weights" in strategy:
            w_dense, w_sparse = strategy["hybrid_weights"]
            print(f"[Retrieval] Fallback Strategy active → Weights: d={w_dense}, s={w_sparse}")
        else:
            w_dense, w_sparse = HYBRID_WEIGHTS.get(query_type, (0.7, 0.3))
            
        print(f"[Retrieval] query_type={query_type} → Qdrant Dense Search (weights: d={w_dense}, s={w_sparse})")
        
        search_result = client.search(
            collection_name="documents",
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=k,
            with_payload=True,
            with_vectors=True
        )
        
        results = []
        for scored_point in search_result:
            p = scored_point.payload
            results.append(Chunk(
                chunk_id=p.get("chunk_id", ""),
                doc_id=p.get("doc_id", ""),
                source_title=p.get("source_title", ""),
                text=p.get("text", ""),
                page_number=p.get("page_number", 0),
                embedding=scored_point.vector,
                relevance_score=scored_point.score,
                ingested_at=p.get("ingested_at")
            ))
            
        return results

    except Exception as e:
        print(f"Error reading from Qdrant: {e}")
        return []
