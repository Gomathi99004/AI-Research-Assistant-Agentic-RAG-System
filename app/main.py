from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import ask, upload
from app.core.db import get_collection

@asynccontextmanager
async def lifespan(app: FastAPI):
    # GAP 15: Create MongoDB indexes at startup for fast source_title filtering
    try:
        collection = get_collection()
        collection.create_index("source_title")
        collection.create_index([("chunk_id", 1)], unique=True)
        print("✅ MongoDB indexes ensured.")
    except Exception as e:
        print(f"⚠️  MongoDB index creation skipped: {e}")
    yield

app = FastAPI(title="AI Research Assistant", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In prod, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}
