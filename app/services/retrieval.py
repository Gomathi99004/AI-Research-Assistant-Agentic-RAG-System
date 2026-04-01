import numpy as np
from typing import List
from scipy.spatial.distance import cosine
from sentence_transformers import SentenceTransformer

from app.models.chunk import Chunk
from app.core.config import settings
from app.core.db import get_collection

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.EMBEDDING_MODEL, trust_remote_code=True)
    return _model

async def fetch_chunks(query: str, files: list = None, k: int = 5) -> List[Chunk]:
    chunks_data = []
    try:
        collection = get_collection()

        filter_query = {}
        if files:
            filter_query["source_title"] = {"$in": files}

        chunks_data = list(collection.find(filter_query))
    except Exception as e:
        print(f"Error reading from MongoDB: {e}")
        return []

    if not chunks_data:
        return []

    model_inst = get_model()
    query_embedding = model_inst.encode(query)

    scored_chunks = []
    for c in chunks_data:
        doc_emb = np.array(c["embedding"])

        if np.count_nonzero(doc_emb) == 0 or np.count_nonzero(query_embedding) == 0:
            sim = 0.0
        else:
            sim = 1.0 - cosine(query_embedding, doc_emb)

        if sim >= settings.RETRIEVAL_MIN_SCORE:
            scored_chunks.append((sim, c))

    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    top_candidates = scored_chunks[:k]

    results = []
    for sim, r in top_candidates:
        results.append(Chunk(
            chunk_id=r["chunk_id"],
            doc_id=r["doc_id"],
            source_title=r["source_title"],
            text=r["text"],
            page_number=r.get("page_number"),
            embedding=r["embedding"],
            relevance_score=float(sim),
            ingested_at=r["ingested_at"]
        ))

    return results
