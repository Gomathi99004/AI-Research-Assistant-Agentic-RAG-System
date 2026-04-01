from pydantic import BaseModel
from typing import Optional, List

class SourceRef(BaseModel):
    title: str
    chunk_id: str
    relevance_score: float

class ResearchResponse(BaseModel):
    request_id: str
    summary: str
    key_points: List[str]
    comparison: Optional[str]
    sources: List[SourceRef]
    confidence: float
    low_confidence: bool
    latency_ms: int

class QueryRequest(BaseModel):
    query: str
    files: Optional[List[str]] = None
