# RAG Backend - PDF Q&A System

Minimal RAG backend with FastAPI, Qdrant, PostgreSQL, and Gemini.

## Setup

### 1. Prerequisites
- Python 3.9+
- PostgreSQL running locally
- Qdrant running locally

### 2. Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database
sudo -u postgres psql
CREATE DATABASE claude_rag_db;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE claude_rag_db TO postgres;
\q
```

### 3. Install Qdrant
```bash
# Using Docker (easiest)
docker run -p 6333:6333 qdrant/qdrant

# Or download binary from https://qdrant.tech/documentation/quick-start/
```

### 4. Setup Python Environment
```bash
# Clone/create project directory
mkdir rag-backend && cd rag-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Environment
```bash
# Copy env example
cp .env.example .env

# Edit .env and add your Gemini API key
nano .env
```

### 6. Run Backend
```bash
python api.py
```

Backend runs on `http://localhost:8000`

## API Endpoints

### Upload PDF
```bash
POST /upload
Content-Type: multipart/form-data
Body: file=<pdf_file>
```

### List Documents
```bash
GET /documents
```

### Delete Document
```bash
DELETE /documents/{doc_id}
```

### Create Session
```bash
POST /session
Body: {"session_id": "optional"}
```

### Query RAG
```bash
POST /query
Body: {
  "query": "your question",
  "session_id": "session_id",
  "top_k": 5,
  "doc_filter": null,
  "only_if_sources": false
}
```

### Get Messages
```bash
GET /messages/{session_id}
```

### Clear Session
```bash
DELETE /session/{session_id}
```

## Architecture Choices

**PDF Parser**: PyMuPDF (fitz) - fastest, best text extraction, handles complex PDFs.

**Chunking**: Word-based with overlap, preserves context across chunk boundaries.

**Embeddings**: sentence-transformers (all-MiniLM-L6-v2) - lightweight, fast, good quality.

**Vector DB**: Qdrant - native Python client, easy filtering, HNSW index for speed.

## Testing
```bash
# Test upload
curl -X POST http://localhost:8000/upload -F "file=@test.pdf"

# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query":"What is this about?","session_id":"test123","top_k":5}'
```

## Troubleshooting

**PostgreSQL connection error**: Check credentials in .env, ensure postgres is running.

**Qdrant connection error**: Start Qdrant with `docker run -p 6333:6333 qdrant/qdrant`

**Import errors**: Activate venv and reinstall requirements.