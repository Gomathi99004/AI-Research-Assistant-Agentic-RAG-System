from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import ask, upload

app = FastAPI(title="AI Research Assistant", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In prod, restrict to frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ask.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

@app.get("/health")
def health_check():
    return {"status": "ok"}
