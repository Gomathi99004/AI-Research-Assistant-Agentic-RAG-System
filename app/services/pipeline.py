import json
from app.services.cache import get_cached_response, set_cached_response
from app.agents.graph import run_workflow
from app.services.formatter import state_to_response
from app.models.response import ResearchResponse

import re

def clean_query(q: str):
    # Remove special characters to clean noise before embedding
    return re.sub(r'[^\w\s]', '', q).strip()

async def process_query(query: str, files: list = None) -> ResearchResponse:
    cleaned_query = clean_query(query)
    
    cache_key = f"{cleaned_query}_{'-'.join(sorted(files)) if files else 'all'}"
    cached = await get_cached_response(cache_key)
    
    if cached:
        try:
            data = json.loads(cached)
            return ResearchResponse(**data)
        except Exception:
            pass

    final_state = await run_workflow(cleaned_query, files)
    response = state_to_response(final_state)
    await set_cached_response(cache_key, response.model_dump_json())
    
    return response
