import os
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from app.ingestion.loader import load_pdf
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import embed_chunks
from app.ingestion.vector_store import upsert_chunks
from app.core.db import get_collection

router = APIRouter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        collection = get_collection()

        # GAP 7: Duplicate guard — return early if already indexed
        existing_count = collection.count_documents({"source_title": file.filename})
        if existing_count > 0:
            return {
                "status": "already_indexed",
                "message": f"'{file.filename}' is already in the knowledge base ({existing_count} chunks). Delete it first to re-index.",
                "pages": 0,
                "chunks": existing_count
            }

        # Save permanent file to uploads/ directory
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Run Ingestion Pipeline
        docs = load_pdf(file_path)
        if not docs:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="No extractable text found in PDF. It might be a scanned image.")

        chunks = chunk_text(docs)
        embedded_chunks = embed_chunks(chunks)
        upsert_chunks(embedded_chunks)

        return {
            "status": "success",
            "message": f"Successfully ingested '{file.filename}' into the knowledge base.",
            "pages": len(docs),
            "chunks": len(chunks)
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@router.get("/documents")
async def get_documents():
    try:
        collection = get_collection()
        titles = collection.distinct("source_title")
        documents = [{"title": title} for title in sorted(titles) if title]
        return {"documents": documents}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/documents/view/{filename}")
async def view_document(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="PDF document not found on server.")
    return FileResponse(file_path, media_type="application/pdf")

@router.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document's chunks from MongoDB and its PDF file from disk."""
    try:
        collection = get_collection()
        result = collection.delete_many({"source_title": filename})

        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "status": "success",
            "message": f"Deleted '{filename}' and {result.deleted_count} associated chunks.",
            "chunks_removed": result.deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")
