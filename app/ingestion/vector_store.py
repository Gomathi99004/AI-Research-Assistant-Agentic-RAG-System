import uuid
from typing import List, Dict
from qdrant_client.models import PointStruct, VectorParams, Distance
from app.core.qdrant_client import get_qdrant_client

COLLECTION_NAME = "documents"

def init_qdrant_collection():
    client = get_qdrant_client()
    try:
        # Check if exists
        client.get_collection(COLLECTION_NAME)
    except Exception:
        # Create if not exists. BGE-Large uses 1024 dimensions.
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
        )

def upsert_chunks(chunks: List[Dict]):
    if not chunks:
        return
        
    try:
        client = get_qdrant_client()
        init_qdrant_collection()
        
        points = []
        for c in chunks:
            # Qdrant requires UUID or Int as ID.
            # Convert our chunk_id to UUID or generate a new one based on chunk_id
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, c["chunk_id"]))
            
            points.append(PointStruct(
                id=point_id,
                vector=c["embedding"],
                payload={
                    "chunk_id": c["chunk_id"],
                    "doc_id": c["doc_id"],
                    "source_title": c["source_title"],
                    "text": c["text"],
                    "page_number": c["page_number"]
                }
            ))
            
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        print(f"Successfully upserted {len(points)} chunks into Qdrant collection '{COLLECTION_NAME}'.")
    except Exception as e:
        print(f"Failed to upsert to Qdrant: {e}")
        raise
