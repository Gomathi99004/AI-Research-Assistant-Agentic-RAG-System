"""
Shared MongoDB client singleton.
Import `get_collection` wherever you need DB access — never create MongoClient directly in route handlers.
"""
import pymongo
from app.core.config import settings

_client: pymongo.MongoClient = None

def get_client() -> pymongo.MongoClient:
    global _client
    if _client is None:
        _client = pymongo.MongoClient(settings.MONGODB_URI)
    return _client

def get_collection():
    client = get_client()
    db = client[settings.MONGODB_DB_NAME]
    return db[settings.MONGODB_COLLECTION]
