import os
from qdrant_client import QdrantClient

_qdrant_client = None

def get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        # User requested local disk mode (no Docker)
        # We will store Qdrant data in the local data directory
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "qdrant_data")
        os.makedirs(data_dir, exist_ok=True)
        _qdrant_client = QdrantClient(path=data_dir)
    return _qdrant_client
