from typing import TypedDict, List, Optional
from app.models.chunk import Chunk
from app.models.response import ResearchResponse

class AgentState(TypedDict):
    query: str
    query_type: str
    expanded_queries: List[str]
    sub_queries: List[str]
    chunks: List[Chunk]
    filtered_chunks: List[Chunk]
    compressed_context: str
    retrieval_quality: str
    summary: str
    key_points: List[str]
    comparison: Optional[str]
    confidence: float
    grounding_score: float
    retry_count: int
    re_retrieve_count: int
    hop_count: int
    failure_memory: List[str]
    retrieval_strategy: dict
    reasoning_trace: List[str]
    final_response: Optional[ResearchResponse]
    files: Optional[List[str]]
