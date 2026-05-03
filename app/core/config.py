from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # LLM Providers
    GROQ_API_KEYS: str
    GEMINI_API_KEYS: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # NLP Ranking
    RERANKER_MODEL: str = "BAAI/bge-reranker-large"
    
    # Vector Store
    MONGODB_URI: str = "mongodb://localhost:27017/"
    VECTOR_STORE: str = "mongodb"
    LOCAL_STORE_PATH: str = "local_store.pkl"
    MONGODB_DB_NAME: str = "rag_db"
    MONGODB_COLLECTION: str = "chunks"

    # Retrieval
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_MIN_SCORE: float = 0.40
    RETRIEVAL_MODE: str = "hybrid"
    EMBEDDING_MODEL: str = "BAAI/bge-large-en-v1.5"

    # Cache
    REDIS_URL: str = "redis://localhost:6379/0"

    # App
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    @property
    def groq_keys(self) -> List[str]:
        return [k.strip() for k in self.GROQ_API_KEYS.split(",") if k.strip()]
        
    @property
    def gemini_keys(self) -> List[str]:
        return [k.strip() for k in self.GEMINI_API_KEYS.split(",") if k.strip()]

    class Config:
        env_file = ".env"

settings = Settings()
