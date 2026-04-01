import uuid
from typing import List, Dict

def chunk_text(docs: List[Dict], chunk_size: int = 400, overlap: int = 100) -> List[Dict]:
    chunks = []
    for doc in docs:
        text = doc["text"]
        
        words = text.split()
        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "doc_id": "doc_" + doc["source_title"],
                "source_title": doc["source_title"],
                "text": chunk_text,
                "page_number": doc["page_number"]
            })
            
            i += (chunk_size - overlap)
            
    return chunks
