# Agentic RAG Server (FastAPI Backend)

This is the Python-based backend service driving the local Agentic RAG application. It utilizes **FastAPI** for HTTP routing, **sentence-transformers** with local `.pkl` persistence for offline vector search, and **LangGraph** paired with **Groq** and **Google Gemini** for agent-driven self-reflection loops.

## 🛠️ Tech Stack
* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) + Uvicorn
* **Agent Flow:** [LangGraph](https://python.langchain.com/docs/langgraph)
* **LLM Core:** `llama-3.3-70b-versatile` (Groq API array fallback) and `gemini-2.5-flash` (Google API)
* **Embeddings:** `all-mpnet-base-v2` (Bi-Encoder)
* **Re-ranker:** `ms-marco-MiniLM-L-6-v2` (Cross-Encoder)
* **Document Parser:** PyMuPDF (`fitz`) bundled with an AI visual OCR fallback string extractor for scanned documents.

---

## 🚀 Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system along with Pip. 

### 2. Set Up Virtual Environment
First, open your favorite terminal directly inside this `backend/` directory. Create an isolated python container environment so you do not install massive AI packages system-wide.

```powershell
# 1. Create the environment
python -m venv venv

# 2. Activate it (Windows PowerShell)
.\venv\Scripts\activate
```
*(If you are on macOS or Linux, run `source venv/bin/activate` instead)*

### 3. Install Dependencies
With the `(venv)` tag prefix active in your terminal, run:
```powershell
pip install -r requirements.txt
```
*(This install includes PyTorch and Sentence-Transformers, so it may take a few minutes).*

### 4. Configure Environment Variables
You must provide keys in order for the `llm.py` service to hit the external language models.

*Duplicate* the included `.env.example` file and rename it uniquely to `.env`. This `.env` file is protected by the `.gitignore` so your API keys will stay private.

Inside the `.env`, provide comma-separated raw keys:
```ini
GROQ_API_KEYS="gsk_123,gsk_456"
GEMINI_API_KEYS="AIza123,AIza456"
```
*(The system features a robust "round-robin" rotation strategy. It will burn through your Groq keys sequentially for maximum speed, and gracefully fallback to your free Gemini keys perfectly if Groq imposes a rate limit).*

### 5. Running the Live API Server
Once your virtual environment is active and your API keys are registered, boot up the local Uvicorn dev server:

```powershell
uvicorn app.main:app --reload
```

By default, the server pins exactly to **`http://127.0.0.1:8000`**. 

You can instantly test if the server is alive by going to `http://127.0.0.1:8000/health` in your browser.

---

## 📁 Repository Architectural Structure

* **`/app/main.py`** - FastAPI initialization and global CORS router registration.
* **`/app/api/routes`** - Defined Restful POST Endpoints pointing out to the React frontend (`/api/upload`, `/api/ask`).
* **`/app/ingestion/`** - The mathematical pipeline logic reading an uploaded binary PDF, splitting strings, executing `model.encode()`, and saving the vectors to `local_store.pkl`.
* **`/app/services/`** - Isolated functional services for talking to the remote LLM APIs, checking cache states, parsing model answers, and finding nearest string distances locally using SciPy cosine mathematics. 
* **`/app/agents/`** - The deterministic LangGraph nodes (retriever → summarizer → critic loop) acting as the "Brain" to prevent AI hallucinations.
