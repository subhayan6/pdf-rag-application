# 📄 PDF RAG Application

A production-ready Retrieval-Augmented Generation (RAG) system for intelligent PDF question-answering, powered by Google Gemini, Qdrant vector database, and PostgreSQL.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎯 Features

- **📤 Multi-PDF Upload**: Upload and process multiple PDF documents simultaneously
- **🔍 Semantic Search**: Advanced vector similarity search using Qdrant
- **💬 Conversational UI**: Interactive Streamlit chat interface with session management
- **📊 Source Attribution**: Clear citations with document name, page number, and relevance scores
- **⚙️ Configurable Retrieval**: Adjustable Top-K, document filtering, and chunking parameters
- **📈 Performance Metrics**: Query response time and retrieval count tracking
- **🔄 Session Management**: Multiple chat sessions with persistent history
- **🐳 One-Command Deployment**: Docker Compose for instant setup

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                            │
│                     (Streamlit - Port 8501)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│                       (Port 8000)                                │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐    │
│  │ PDF Processor│  │  RAG Engine  │  │  Vector DB Client │    │
│  │  (PyMuPDF)   │  │   (Gemini)   │  │    (Qdrant)       │    │
│  └──────────────┘  └──────────────┘  └───────────────────┘    │
└────────┬────────────────────┬────────────────────┬─────────────┘
         │                    │                    │
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   PostgreSQL    │  │  Gemini API     │  │    Qdrant       │
│   (Port 5432)   │  │  (External)     │  │  (Port 6333)    │
│                 │  │                 │  │                 │
│ • Documents     │  │ • LLM Response  │  │ • Embeddings    │
│ • Sessions      │  │ • Generation    │  │ • Vector Search │
│ • Messages      │  │                 │  │                 │
│ • Metrics       │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Component Overview

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Interactive UI for document upload and chat |
| **Backend API** | FastAPI | REST API for document processing and RAG queries |
| **Vector DB** | Qdrant | Semantic search with cosine similarity |
| **Relational DB** | PostgreSQL | Store documents, sessions, messages, metrics |
| **LLM** | Google Gemini 2.5 Flash | Answer generation with context |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) | Text vectorization |
| **PDF Parser** | PyMuPDF (fitz) | Fast and accurate text extraction |

---

## 🚀 Quick Start (Docker)

### Prerequisites

- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### One-Command Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag-backend
   ```

2. **Create `.env` file**
   ```bash
   cp .env.example .env
   ```

3. **Add your Gemini API key to `.env`**
   ```bash
   # Open .env and replace the placeholder
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. **Start all services**
   ```bash
   docker-compose up --build
   ```

5. **Access the application**
   - 🎨 **Streamlit UI**: http://localhost:8501
   - 🔌 **FastAPI Docs**: http://localhost:8000/docs
   - 🗄️ **Qdrant Dashboard**: http://localhost:6333/dashboard

That's it! 🎉

### Stopping the Application

```bash
docker-compose down
```

To remove volumes (deletes all data):
```bash
docker-compose down -v
```

---

## 💻 Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (running locally)
- Qdrant (running locally or via Docker)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd rag-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Start PostgreSQL** (if not running)
   ```bash
   # Using Docker
   docker run -d --name postgres \
     -e POSTGRES_PASSWORD=password \
     -e POSTGRES_DB=claude_rag_db \
     -p 5432:5432 \
     postgres:15-alpine
   ```

6. **Start Qdrant** (if not running)
   ```bash
   docker run -d --name qdrant \
     -p 6333:6333 -p 6334:6334 \
     qdrant/qdrant:latest
   ```

7. **Run the backend**
   ```bash
   python api.py
   ```

8. **Run the frontend** (in a new terminal)
   ```bash
   streamlit run streamlit_app.py
   ```

9. **Access the application**
   - Frontend: http://localhost:8501
   - Backend: http://localhost:8000/docs

---

## 📁 Project Structure

```
rag-backend/
├── .env.example              # Environment variables template
├── .env                      # Your local configuration (git-ignored)
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker orchestration
├── Dockerfile.backend        # Backend container image
├── Dockerfile.frontend       # Frontend container image
├── README.md                 # This file
│
├── config.py                 # Configuration management
├── db.py                     # PostgreSQL models and session
├── vector_db.py              # Qdrant vector database client
├── pdf_processor.py          # PDF text extraction and chunking
├── rag_engine.py             # RAG pipeline with Gemini
├── api.py                    # FastAPI backend server
└── streamlit_app.py          # Streamlit frontend UI
```

---

## 🎨 Screenshots

### Main Chat Interface
![Chat Interface](screenshots/chat_interface.png)
*Interactive chat with source attribution and relevance scores*

### Document Management
![Document Management](screenshots/document_management.png)
*Upload, view, and delete PDF documents*

### Settings Panel
![Settings](screenshots/settings.png)
*Configure Top-K, document filters, and retrieval options*

### API Documentation
![API Docs](screenshots/api_docs.png)
*Auto-generated FastAPI documentation at /docs*

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | **Required** |
| `POSTGRES_HOST` | PostgreSQL host | `localhost` |
| `POSTGRES_PORT` | PostgreSQL port | `5432` |
| `POSTGRES_DB` | Database name | `claude_rag_db` |
| `POSTGRES_USER` | Database username | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `password` |
| `QDRANT_HOST` | Qdrant host | `localhost` |
| `QDRANT_PORT` | Qdrant port | `6333` |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | Words per chunk | `512` |
| `CHUNK_OVERLAP` | Overlapping words | `50` |
| `TOP_K` | Default retrieval count | `5` |

### Chunking Strategy

The application uses a **word-based sliding window** with overlap:

- **CHUNK_SIZE=512**: Each chunk contains ~512 words (optimal for semantic coherence)
- **CHUNK_OVERLAP=50**: 50 words overlap between consecutive chunks (maintains context)

**Why this approach?**
- ✅ Preserves sentence boundaries better than character-based chunking
- ✅ Overlap prevents information loss at chunk boundaries
- ✅ Balanced between context size and retrieval precision

### Embedding Model Options

| Model | Dimensions | Speed | Quality |
|-------|-----------|-------|---------|
| `all-MiniLM-L6-v2` | 384 | ⚡⚡⚡ Fast | ⭐⭐⭐ Good |
| `all-mpnet-base-v2` | 768 | ⚡⚡ Medium | ⭐⭐⭐⭐ Better |
| `multi-qa-mpnet-base-dot-v1` | 768 | ⚡⚡ Medium | ⭐⭐⭐⭐⭐ Best |

---

## 🔍 How It Works

### 1. Document Upload & Processing

```
PDF Upload → PyMuPDF Extraction → Text Chunking → Embedding Generation → Qdrant Storage
```

1. User uploads PDF via Streamlit
2. PyMuPDF extracts text page by page
3. Text is chunked with sliding window (512 words, 50 overlap)
4. Each chunk is embedded using sentence-transformers
5. Embeddings stored in Qdrant with metadata (filename, page, doc_id)
6. Document metadata saved in PostgreSQL

### 2. RAG Query Pipeline

```
User Query → Embed Query → Vector Search → Retrieve Top-K → Build Context → LLM Generation → Answer + Citations
```

1. User submits question
2. Query is embedded using same model
3. Qdrant performs cosine similarity search
4. Top-K most relevant chunks retrieved
5. Context built from chunks with source metadata
6. Prompt sent to Gemini with context and query
7. LLM generates answer with citations
8. Response displayed with sources and relevance scores

### 3. Why PyMuPDF?

**Chosen over alternatives** (pdfplumber, PyPDF2) for:
- ⚡ **Speed**: 10x faster text extraction
- 🎯 **Accuracy**: Better handling of complex layouts
- 📦 **Lightweight**: Minimal dependencies
- 🔧 **Reliability**: Production-proven for large documents

---

## 📊 Database Schema

### PostgreSQL Tables

**documents**
- `id` (PK): Auto-incrementing ID
- `filename`: Original PDF filename
- `upload_time`: Upload timestamp
- `status`: processing | completed | failed
- `page_count`: Number of pages
- `meta`: JSON metadata

**chat_sessions**
- `id` (PK): Auto-incrementing ID
- `session_id` (Unique): UUID
- `created_at`: Session creation time
- `meta`: JSON metadata

**chat_messages**
- `id` (PK): Auto-incrementing ID
- `session_id`: Foreign key to session
- `role`: user | assistant
- `content`: Message text
- `timestamp`: Message time
- `sources`: JSON array of retrieved chunks
- `meta`: JSON metadata

**query_metrics**
- `id` (PK): Auto-incrementing ID
- `session_id`: Associated session
- `query`: User query text
- `response_time`: Time in seconds
- `retrieval_count`: Number of chunks retrieved
- `llm_tokens`: Tokens used (optional)
- `timestamp`: Query time
- `meta`: JSON metadata

### Qdrant Collection

**pdf_chunks**
- `id`: UUID
- `vector`: 384-dim embedding (all-MiniLM-L6-v2)
- `payload`:
  - `text`: Chunk content
  - `page`: Page number
  - `doc_id`: Document ID (FK to PostgreSQL)
  - `filename`: Source document
  - `chunk_id`: Sequential chunk index

---

## 🧪 Testing

### Test PDF Upload
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@test.pdf"
```

### Test RAG Query
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the main topic?",
    "session_id": "test-session",
    "top_k": 5
  }'
```

### View API Documentation
Visit: http://localhost:8000/docs

---

## 🐛 Troubleshooting

### Docker Issues

**Problem**: Containers fail to start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart
```

**Problem**: Port already in use
```bash
# Change ports in docker-compose.yml
ports:
  - "8501:8501"  # Change first number (host port)
```

### API Connection Issues

**Problem**: Frontend can't connect to backend
- Check backend is running: http://localhost:8000/docs
- Verify `API_URL` in docker-compose.yml for frontend service
- For local dev, ensure both services are running

### Database Issues

**Problem**: Database connection refused
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Verify credentials in .env
# Check POSTGRES_HOST (localhost for local, postgres for Docker)
```

### Qdrant Issues

**Problem**: Collection not found
```bash
# Qdrant creates collections automatically
# If issues persist, restart Qdrant:
docker restart qdrant
```

---

## 📈 Performance Optimization

### 1. Chunk Size Tuning
- **Smaller chunks** (256-384 words): Better precision, more granular
- **Larger chunks** (512-768 words): Better context, fewer chunks

### 2. Top-K Selection
- **Lower K** (3-5): Faster, more focused
- **Higher K** (7-10): More comprehensive, slower

### 3. Embedding Model
- Switch to `all-mpnet-base-v2` for better quality (2x slower)
- Use `all-MiniLM-L6-v2` for speed (production-ready)

### 4. Database Optimization
- Add indexes on frequently queried columns
- Use connection pooling (already configured)
- Regular VACUUM on PostgreSQL

---

## 🔒 Security Considerations

### Production Checklist

- [ ] Change default PostgreSQL password
- [ ] Use secrets management for API keys (not .env in production)
- [ ] Enable HTTPS/TLS for API endpoints
- [ ] Implement rate limiting on /upload and /query endpoints
- [ ] Add authentication/authorization
- [ ] Sanitize file uploads (validate PDFs)
- [ ] Set up CORS properly (restrict origins)
- [ ] Use environment-specific configurations
- [ ] Enable logging and monitoring
- [ ] Regular security updates for dependencies

---

## 📝 API Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload a PDF file |
| `GET` | `/documents` | List all documents |
| `DELETE` | `/documents/{id}` | Delete a document |

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/session` | Create/get session |
| `GET` | `/sessions` | List all sessions |
| `GET` | `/messages/{session_id}` | Get session messages |
| `DELETE` | `/session/{session_id}` | Clear session messages |

### RAG

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/query` | Submit RAG query |

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **FastAPI**: Modern web framework for building APIs
- **Streamlit**: Rapid UI development for data apps
- **Qdrant**: High-performance vector database
- **Google Gemini**: State-of-the-art LLM
- **sentence-transformers**: Efficient embedding models
- **PyMuPDF**: Fast PDF text extraction

---

## 📧 Contact

For questions or issues, please open a GitHub issue or contact the maintainer.

---

## 🔄 Changelog

### v1.0.0 (2024-10-08)
- Initial release
- PDF upload and processing
- RAG-powered Q&A with Gemini
- Session management
- Docker deployment
- Comprehensive documentation

---

**Made with ❤️ for intelligent document understanding**