from app.services.llm import call_llm
import numpy as np

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

def extract_keywords(text: str) -> set:
    """Very naive keyword extraction (just words > 4 chars)."""
    words = text.lower().replace(".", "").replace(",", "").split()
    return set(w for w in words if len(w) > 4)

async def detect_contradiction(answer: str, context: str) -> float:
    """Uses LLM to detect if answer contradicts context. Returns 1.0 if contradicts, 0.0 if safe."""
    prompt = f"""Does the Answer explicitly contradict the facts in the Context?
Answer: {answer}
Context: {context}

Reply with exactly ONE word: YES or NO.
"""
    try:
        response = await call_llm(prompt, max_tokens=5)
        if "yes" in response.lower():
            return 1.0
    except Exception:
        pass
    return 0.0

async def calculate_grounding_score(answer: str, context: str) -> float:
    if not answer or not context:
        return 0.0
        
    try:
        # 1. Semantic Similarity
        model = get_model()
        ans_emb = model.encode(answer)
        ctx_emb = model.encode(context)
        semantic_sim = max(0.0, cosine_similarity(ans_emb, ctx_emb))
        
        # 2. Keyword Overlap
        ans_kw = extract_keywords(answer)
        ctx_kw = extract_keywords(context)
        overlap = len(ans_kw.intersection(ctx_kw))
        keyword_overlap_score = overlap / len(ans_kw) if ans_kw else 1.0
        
        # 3. Contradiction Penalty
        contradiction = await detect_contradiction(answer, context)
        
        # Weighted formula
        score = (0.6 * semantic_sim) + (0.3 * keyword_overlap_score) - (0.1 * contradiction)
        return max(0.0, min(1.0, score))
        
    except Exception as e:
        print(f"[Grounding] Calculation failed: {e}")
        return 0.5 # Safe neutral fallback

async def adversarial_verify(answer: str, context: str) -> dict:
    """
    Uses a faster LLM to actively try to disprove the answer using the context.
    Returns {"adversarial_fail": bool, "reason": str}
    """
    prompt = f"""You are an aggressive adversarial fact-checker. 
Your goal is to DISPROVE the following Answer using ONLY the provided Context.
Look for:
1. Missing citations or evidence for claims made in the Answer.
2. Unsupported statements not found in the Context.
3. Conflicting evidence between the Answer and the Context.

Answer: {answer}
Context: {context}

If the Answer is fully supported and you cannot disprove it, reply with exactly: "PASS".
If you find ANY unsupported claim or contradiction, reply with "FAIL: " followed by a brief 1-sentence reason.
"""
    try:
        # Use fast_mode=True to use the smaller/faster model
        response = await call_llm(prompt, max_tokens=100, fast_mode=True)
        response_clean = response.strip()
        
        if response_clean.startswith("FAIL"):
            reason = response_clean[5:].strip() if len(response_clean) > 5 else "Unsupported claims detected."
            return {"adversarial_fail": True, "reason": reason}
            
        return {"adversarial_fail": False, "reason": ""}
        
    except Exception as e:
        print(f"[Grounding] Adversarial verify failed: {e}")
        return {"adversarial_fail": False, "reason": "Verification error"}
