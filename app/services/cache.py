import hashlib
try:
    import redis.asyncio as redis
except ImportError:
    pass
from app.core.config import settings

redis_client = None
if settings.REDIS_URL:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    except NameError:
        redis_client = None

def get_cache_key(query: str) -> str:
    normalized = query.lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()

async def get_cached_response(query: str) -> str | None:
    if not redis_client:
        return None
    key = get_cache_key(query)
    try:
        return await redis_client.get(key)
    except Exception:
        return None

async def set_cached_response(query: str, response_json: str):
    if not redis_client:
        return
    key = get_cache_key(query)
    try:
        await redis_client.setex(key, 3600, response_json)
    except Exception:
        pass
