import uuid
import re
from typing import List, Dict

def chunk_text(docs: List[Dict], max_chunk_size: int = 500) -> List[Dict]:
    chunks = []
    for doc in docs:
        text = doc["text"]
        
        # Split by double newline to get paragraphs (semantic blocks)
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_chunk_text = ""
        
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
                
            # If adding this paragraph exceeds our soft max limit, push the current chunk
            if current_chunk_text and len(current_chunk_text.split()) + len(p.split()) > max_chunk_size:
                chunks.append({
                    "chunk_id": str(uuid.uuid4()),
                    "doc_id": "doc_" + doc["source_title"],
                    "source_title": doc["source_title"],
                    "text": current_chunk_text.strip(),
                    "page_number": doc["page_number"],
                    "metadata": "paragraph_block"
                })
                current_chunk_text = p
            else:
                if current_chunk_text:
                    current_chunk_text += "\n\n" + p
                else:
                    current_chunk_text = p
                    
        # Push remainder
        if current_chunk_text:
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "doc_id": "doc_" + doc["source_title"],
                "source_title": doc["source_title"],
                "text": current_chunk_text.strip(),
                "page_number": doc["page_number"],
                "metadata": "paragraph_block"
            })
            
    return chunks
