import argparse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.ingestion.loader import load_pdf
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import embed_chunks
from app.ingestion.vector_store import upsert_chunks

def run_ingestion(file_path: str):
    print(f"Loading PDF: {file_path}")
    docs = load_pdf(file_path)
    print(f"Extracted {len(docs)} pages.")
    
    print("Chunking text...")
    chunks = chunk_text(docs)
    print(f"Created {len(chunks)} chunks.")
    
    print("Generating embeddings (this might take a moment)...")
    embedded_chunks = embed_chunks(chunks)
    
    print("Upserting to Local Vector Store...")
    upsert_chunks(embedded_chunks)
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a PDF document into Local Vector Store")
    parser.add_argument("--source", required=True, help="Path to the PDF file")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source):
        print(f"Error: File not found at {args.source}")
        sys.exit(1)
        
    run_ingestion(args.source)
