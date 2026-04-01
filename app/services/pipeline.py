import json
from app.services.cache import get_cached_response, set_cached_response
from app.agents.graph import run_workflow
from app.services.formatter import state_to_response
from app.models.response import ResearchResponse

import re

def clean_query(q: str):
    # Remove special characters to clean noise before embedding
    return re.sub(r'[^\w\s]', '', q).strip()

async def process_query(query: str) -> ResearchResponse:
    cleaned_query = clean_query(query)
    cached = await get_cached_response(cleaned_query)
    if cached:
        try:
            data = json.loads(cached)
            return ResearchResponse(**data)
        except Exception:
            pass

    final_state = await run_workflow(cleaned_query)
    response = state_to_response(final_state)
    await set_cached_response(cleaned_query, response.model_dump_json())
    
    return response
