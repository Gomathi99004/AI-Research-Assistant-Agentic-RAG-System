from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # LLM Providers
    GROQ_API_KEYS: str
    GEMINI_API_KEYS: str

    # Vector Store
    MONGODB_URI: str = ''
    VECTOR_STORE: str = "local"
    LOCAL_STORE_PATH: str = "local_store.pkl"

    # Retrieval
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_MIN_SCORE: float = 0.40
    RETRIEVAL_MODE: str = "hybrid"
    EMBEDDING_MODEL: str = "all-mpnet-base-v2"

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
