from typing import List
from app.services.llm import call_llm

async def compress_context(chunks: list, query: str) -> str:
    """
    Takes the top retrieved chunks and uses the LLM to merge and compress
    them into a single dense knowledge block, removing redundancy.
    """
    if not chunks:
        return ""

    raw_context = "\n\n---\n\n".join([
        f"[SOURCE: {getattr(c, 'source_title', 'Unknown')} | Page {getattr(c, 'page_number', '?')}]\n{getattr(c, 'text', '')}"
        for c in chunks
    ])

    prompt = f"""You are a context compression engine for a research assistant.
You have been given multiple text excerpts retrieved from documents in response to a query.

Your job:
1. Remove any redundant or duplicate information across the excerpts.
2. Merge overlapping facts into single concise statements.
3. Preserve all unique facts, definitions, and data points.
4. Maintain source attribution (e.g., "According to [filename]...").
5. Output ONLY the compressed knowledge block — no commentary.

Query: {query}

Retrieved Excerpts:
{raw_context}
"""
    try:
        compressed = await call_llm(prompt, max_tokens=1500)
        return compressed.strip()
    except Exception as e:
        print(f"[Compressor] LLM compression failed: {e}. Using raw context.")
        # Fallback: just concatenate raw text
        return "\n\n".join([getattr(c, "text", "") for c in chunks])
