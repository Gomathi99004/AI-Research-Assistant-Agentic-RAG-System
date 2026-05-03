🧠 AI Research Assistant — Agentic RAG System

A production-grade, **local-first** Retrieval-Augmented Generation (RAG) system powered by a **LangGraph agentic workflow**, **MongoDB vector store**, **Groq + Gemini LLM**, and a premium **React + Framer Motion** frontend.

> Upload your PDF knowledge base → Select documents → Ask questions → Get structured, source-grounded answers with automatic comparative analysis across files.

---

✨ Features

* 📄 **PDF Upload & Ingestion** — Drag & drop PDFs, extract text with AI OCR fallback (Gemini Vision for scanned pages)
* 🗄️ **Local Qdrant Vector Store** — Persistent vector storage with cosine similarity retrieval
* 🤖 **Self-Correcting Agentic Pipeline**

  * Classifier → Expansion → Retriever → Compressor → Summarizer → Verifier → Comparator → Failure Analysis
* 🛡️ **Adversarial Verification** — Grounding score + fact-check loop
* 🔄 **Fallback Strategy** — Query expansion, sparse fallback, increased search depth
* 🔍 **Document Isolation** — Query selected PDFs only
* 📊 **Comparative Analysis** — Detects conflicts across documents
* 🗑️ **Document Management** — Full deletion (DB + vectors + disk)
* 📑 **Inline PDF Viewer**
* 🎨 **Premium UI** — Framer Motion + responsive layout
* ⚡ **LLM Fallback** — Groq → Gemini

---

🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                │
│  Upload │ Sidebar │ Query + Answer                     │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                   FastAPI Backend                       │
│                                                         │
│  LangGraph Agent Flow:                                  │
│  Classifier → Expansion → Retriever → Compressor        │
│       ↓                     ↑                            │
│  Comparator ← Verifier ← Summarizer                     │
│                    ↓                                    │
│             Failure Analysis                            │
│                                                         │
│  LLMs: Groq (llama-3.3-70b) → Gemini fallback           │
│  Embeddings: all-mpnet-base-v2                          │
└─────────┬───────────────────────────────┬───────────────┘
          │                               │
     Qdrant (Vectors)                MongoDB (Metadata)
```

---

🚀 Quick Start

Prerequisites

* Python 3.11+
* Node.js 18+
* MongoDB (`mongodb://localhost:27017/`)
* Redis (optional)

---

1. Clone Repo

```bash
git clone <your-repo-url>
cd rag
```

---

2. Backend Setup

```bash
cd backend
python -m venv venv
```

**Activate:**

Windows:

```bash
.\venv\Scripts\activate
```

Mac/Linux:

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEYS=your_keys
GEMINI_API_KEYS=your_keys
MONGODB_URI=mongodb://localhost:27017/
```

Run backend:

```bash
uvicorn app.main:app --reload
```

---

3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

⚙️ Environment Variables

| Variable        | Description          |
| --------------- | -------------------- |
| GROQ_API_KEYS   | Groq API keys        |
| GEMINI_API_KEYS | Gemini fallback keys |
| GROQ_MODEL      | Default Groq model   |
| GEMINI_MODEL    | Gemini model         |
| EMBEDDING_MODEL | SentenceTransformer  |
| MONGODB_URI     | MongoDB connection   |
| RETRIEVAL_TOP_K | Retrieved chunks     |
| REDIS_URL       | Optional cache       |

---

📡 API Endpoints

| Method | Endpoint                       | Description |
| ------ | ------------------------------ | ----------- |
| POST   | /api/ask                       | Query       |
| POST   | /api/upload                    | Upload PDF  |
| GET    | /api/documents                 | List docs   |
| GET    | /api/documents/view/{filename} | View PDF    |
| DELETE | /api/documents/{filename}      | Delete      |
| GET    | /health                        | Health      |

Example

```json
{
  "query": "Explain Knowledge-Based Systems",
  "files": ["SQL-Manual.pdf"]
}
```

---

🗂️ Structure

```
rag/
├── backend/
│   ├── app/
│   ├── uploads/
│   ├── qdrant_data/
│   └── requirements.txt
├── frontend/
│   └── src/
└── README.md
```

---

🔒 Security

* Do not commit `.env`
* Restrict CORS in production

---

📝 License

MIT
