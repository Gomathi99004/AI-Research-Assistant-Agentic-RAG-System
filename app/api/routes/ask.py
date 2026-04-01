import time
from fastapi import APIRouter, HTTPException
from app.api.schemas import QueryRequest, ResearchResponse
from app.services.pipeline import process_query

router = APIRouter()

@router.post("/ask", response_model=ResearchResponse)
async def ask_question(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    if len(request.query) > 2000:
        raise HTTPException(status_code=400, detail="Query exceeds 2000 characters")
        
    start_time = time.time()
    try:
        response = await process_query(request.query)
        response.latency_ms = int((time.time() - start_time) * 1000)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
