import os
import pickle
from datetime import datetime
from typing import List, Dict
from app.core.db import get_collection

def upsert_chunks(chunks: List[Dict]):
    if not chunks:
        return
        
    try:
        collection = get_collection()
        
        upserted = 0
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
            # Upsert keyed on chunk_id — prevents duplicate chunks on re-upload
            collection.update_one(
                {"chunk_id": c["chunk_id"]},
                {"$set": doc},
                upsert=True
            )
            upserted += 1
            
        print(f"Successfully upserted {upserted} chunks into MongoDB collection.")
    except Exception as e:
        print(f"Failed to upsert to MongoDB: {e}")
        raise
