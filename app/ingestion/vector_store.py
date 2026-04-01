import os
import pickle
from datetime import datetime
from typing import List, Dict
from app.core.config import settings

def upsert_chunks(chunks: List[Dict]):
    store_path = settings.LOCAL_STORE_PATH
    
    existing_chunks = []
    if os.path.exists(store_path):
        try:
            with open(store_path, "rb") as f:
                existing_chunks = pickle.load(f)
        except Exception as e:
            print(f"Error loading existing local store: {e}")
            existing_chunks = []
            
    documents = []
    for c in chunks:
        doc = {
            "chunk_id": c["chunk_id"],
            "doc_id": c["doc_id"],
            "source_title": c["source_title"],
            "text": c["text"],
            "page_number": c["page_number"],
            "embedding": c["embedding"],
            "ingested_at": datetime.utcnow()
        }
        documents.append(doc)
        
    existing_chunks.extend(documents)
    
    try:
        with open(store_path, "wb") as f:
            pickle.dump(existing_chunks, f)
        print(f"Successfully appended {len(documents)} chunks to the local store ({store_path}).")
    except Exception as e:
        print(f"Failed to write to local store: {e}")
