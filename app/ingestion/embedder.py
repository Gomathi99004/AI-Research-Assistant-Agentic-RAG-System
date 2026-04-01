from typing import List, Dict
from app.core.config import settings

from sentence_transformers import SentenceTransformer

model = None
def get_model():
    global model
    if model is None:
        model_name = getattr(settings, "EMBEDDING_MODEL", "all-mpnet-base-v2")
        model = SentenceTransformer(model_name, trust_remote_code=True)
    return model

def embed_chunks(chunks: List[Dict], batch_size: int = 64) -> List[Dict]:
    model = get_model()
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts = [c["text"] for c in batch]
        embeddings = model.encode(texts).tolist()
        
        for j, emb in enumerate(embeddings):
            batch[j]["embedding"] = emb
            
    return chunks
