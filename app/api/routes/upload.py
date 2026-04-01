import os
import tempfile
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.ingestion.loader import load_pdf
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import embed_chunks
from app.ingestion.vector_store import upsert_chunks

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
            
        # Run Ingestion Pipeline
        docs = load_pdf(tmp_path)
        if not docs:
            os.unlink(tmp_path)
            raise HTTPException(status_code=400, detail="No extractable text found in PDF. It might be a scanned image.")
            
        chunks = chunk_text(docs)
        embedded_chunks = embed_chunks(chunks)
        upsert_chunks(embedded_chunks)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return {
            "status": "success",
            "message": f"Successfully ingested {file.filename} into the local knowledge base.",
            "pages": len(docs),
            "chunks": len(chunks)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
