from app.services.llm import call_llm
import numpy as np

# Rule-based logic lists
COMPARISON_KEYWORDS = ["compare", "difference", "vs", "versus", "contrast"]
MULTI_HOP_PATTERNS = ["impact of", "relationship between", "how does", "why does"]
KEYWORD_HEAVY_SIGNALS = ["define", "what is", "list", "name"]

# Prototypes for embedding fallback (pre-calculated if possible, but we'll use a fast model)
PROTOTYPES = {
    "factual": ["What is X?", "Define Y"],
    "conceptual": ["Explain how X works", "Why does Y happen"],
    "comparison": ["Compare X and Y", "Difference between A and B"],
    "multi-hop": ["Impact of X on Y", "Relationship between A and B"]
}

_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        from app.core.config import settings
        _model = SentenceTransformer(settings.EMBEDDING_MODEL, trust_remote_code=True)
    return _model

def cosine_similarity(a, b):
    if np.count_nonzero(a) == 0 or np.count_nonzero(b) == 0:
        return 0.0
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

async def classify_query(query: str) -> str:
    """
    Uses deterministic rules + embedding similarity to classify a query.
    Fallback to 'conceptual' if uncertain.
    """
    query_lower = query.lower()

    # 1. Rule-based checks
    if any(kw in query_lower for kw in COMPARISON_KEYWORDS):
        return "comparison"
    
    if any(pat in query_lower for pat in MULTI_HOP_PATTERNS):
        return "multi-hop"
        
    if any(sig in query_lower for sig in KEYWORD_HEAVY_SIGNALS) or len(query.split()) <= 3:
        # Very short queries or explicit definition requests
        return "factual"

    # 2. Embedding Fallback
    try:
        model = get_model()
        query_emb = model.encode(query)
        
        best_type = "conceptual"
        best_score = -1.0
        
        for q_type, examples in PROTOTYPES.items():
            for ex in examples:
                ex_emb = model.encode(ex)
                score = cosine_similarity(query_emb, ex_emb)
                if score > best_score:
                    best_score = score
                    best_type = q_type
                    
        # If the best score is reasonably high, trust it
        if best_score > 0.6:
            return best_type
            
    except Exception as e:
        print(f"[Classifier] Embedding fallback failed: {e}")

    # 3. Default
    return "conceptual"
