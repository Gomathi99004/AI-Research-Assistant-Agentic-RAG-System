import uuid
from app.agents.state import AgentState
from app.models.response import ResearchResponse, SourceRef

def state_to_response(state: AgentState) -> ResearchResponse:
    seen_chunks = set()
    sources = []
    
    for chunk in state.get("filtered_chunks", []):
        if getattr(chunk, 'chunk_id', chunk) not in seen_chunks:
            seen_chunks.add(chunk.chunk_id)
            sources.append(SourceRef(
                title=chunk.source_title,
                chunk_id=chunk.chunk_id,
                relevance_score=chunk.relevance_score
            ))
            
    confidence = state.get("confidence", 0.0)
    
    return ResearchResponse(
        request_id=str(uuid.uuid4()),
        summary=state.get("summary", "No summary generated."),
        key_points=state.get("key_points", []),
        comparison=state.get("comparison"),
        sources=sources,
        confidence=confidence,
        low_confidence=confidence < 0.75,
        latency_ms=0
    )
