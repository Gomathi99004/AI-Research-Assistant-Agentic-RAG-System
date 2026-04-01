from typing import TypedDict, List, Optional
from app.models.chunk import Chunk
from app.models.response import ResearchResponse

class AgentState(TypedDict):
    query: str
    sub_queries: List[str]
    chunks: List[Chunk]
    filtered_chunks: List[Chunk]
    summary: str
    key_points: List[str]
    comparison: Optional[str]
    confidence: float
    retry_count: int
    final_response: Optional[ResearchResponse]
