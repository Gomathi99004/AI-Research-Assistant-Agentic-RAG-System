from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

@dataclass
class Chunk:
    chunk_id: str           # UUID
    doc_id: str
    source_title: str
    text: str               # raw chunk content
    page_number: Optional[int]
    embedding: List[float]  # 384-dim
    relevance_score: float  # populated post-retrieval
    ingested_at: datetime
