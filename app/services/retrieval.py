import os
import pickle
import numpy as np
from typing import List
from scipy.spatial.distance import cosine
from sentence_transformers import SentenceTransformer

from app.models.chunk import Chunk
from app.core.config import settings

model = None

def get_model():
    global model
    if model is None:
        model_name = getattr(settings, "EMBEDDING_MODEL", "all-mpnet-base-v2")
        model = SentenceTransformer(model_name, trust_remote_code=True)
    return model

async def fetch_chunks(query: str, k: int = 5) -> List[Chunk]:
    store_path = settings.LOCAL_STORE_PATH
    
    if not os.path.exists(store_path):
        print(f"Local store {store_path} not found. Returning empty chunks.")
        return []

    try:
        with open(store_path, "rb") as f:
            chunks_data = pickle.load(f)
    except Exception as e:
        print(f"Error reading local store: {e}")
        return []
        
    if not chunks_data:
        return []

    model_inst = get_model()
    # SentenceTransformer encode returns a numpy array by default
    query_embedding = model_inst.encode(query)

    scored_chunks = []
    for c in chunks_data:
        doc_emb = np.array(c["embedding"])
        
        if np.count_nonzero(doc_emb) == 0 or np.count_nonzero(query_embedding) == 0:
            sim = 0.0
        else:
            # 1 - cosine distance = cosine similarity
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
