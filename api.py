# from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from typing import Optional, List
# import shutil
# import os
# import uuid
# from datetime import datetime
#
# from db import init_db, get_db, Document, ChatSession, ChatMessage, QueryMetric
# from pdf_processor import pdf_proc
# from vector_db import vdb
# from rag_engine import rag
#
# app = FastAPI()
# app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
#                    allow_headers=["*"])
#
# os.makedirs("uploads", exist_ok=True)
#
#
# @app.on_event("startup")
# def startup():
#     init_db()
#
#
# class QueryRequest(BaseModel):
#     query: str
#     session_id: str
#     top_k: Optional[int] = 5
#     doc_filter: Optional[int] = None
#     only_if_sources: Optional[bool] = False
#
#
# class SessionRequest(BaseModel):
#     session_id: Optional[str] = None
#
#
# @app.post("/upload")
# async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     try:
#         file_path = f"uploads/{uuid.uuid4()}_{file.filename}"
#         with open(file_path, "wb") as f:
#             shutil.copyfileobj(file.file, f)
#
#         doc = Document(filename=file.filename, status="processing")
#         db.add(doc)
#         db.commit()
#         db.refresh(doc)
#
#         chunks, page_count = pdf_proc.process(file_path)
#         vdb.add_chunks(chunks, doc.id, file.filename)
#
#         doc.status = "completed"
#         doc.page_count = page_count
#         db.commit()
#
#         os.remove(file_path)
#         return {"id": doc.id, "filename": file.filename, "status": "completed", "page_count": page_count}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @app.get("/documents")
# def get_documents(db: Session = Depends(get_db)):
#     docs = db.query(Document).all()
#     return [{"id": d.id, "filename": d.filename, "status": d.status, "page_count": d.page_count,
#              "upload_time": d.upload_time} for d in docs]
#
#
# @app.delete("/documents/{doc_id}")
# def delete_document(doc_id: int, db: Session = Depends(get_db)):
#     doc = db.query(Document).filter(Document.id == doc_id).first()
#     if not doc:
#         raise HTTPException(status_code=404, detail="Document not found")
#     vdb.delete_doc(doc_id)
#     db.delete(doc)
#     db.commit()
#     return {"message": "Document deleted"}
#
#
# @app.post("/session")
# def create_session(req: SessionRequest, db: Session = Depends(get_db)):
#     sid = req.session_id or str(uuid.uuid4())
#     existing = db.query(ChatSession).filter(ChatSession.session_id == sid).first()
#     if not existing:
#         session = ChatSession(session_id=sid)
#         db.add(session)
#         db.commit()
#     return {"session_id": sid}
#
#
# @app.get("/sessions")
# def get_sessions(db: Session = Depends(get_db)):
#     sessions = db.query(ChatSession).all()
#     return [{"session_id": s.session_id, "created_at": s.created_at} for s in sessions]
#
#
# @app.get("/messages/{session_id}")
# def get_messages(session_id: str, db: Session = Depends(get_db)):
#     msgs = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp).all()
#     return [{"role": m.role, "content": m.content, "sources": m.sources, "timestamp": m.timestamp} for m in msgs]
#
#
# @app.post("/query")
# def query_rag(req: QueryRequest, db: Session = Depends(get_db)):
#     user_msg = ChatMessage(session_id=req.session_id, role="user", content=req.query)
#     db.add(user_msg)
#     db.commit()
#
#     result = rag.generate_answer(req.query, req.top_k, req.doc_filter, req.only_if_sources)
#
#     assistant_msg = ChatMessage(session_id=req.session_id, role="assistant", content=result["answer"],
#                                 sources=result["sources"])
#     db.add(assistant_msg)
#
#     metric = QueryMetric(session_id=req.session_id, query=req.query, response_time=result["response_time"],
#                          retrieval_count=result["retrieval_count"])
#     db.add(metric)
#
#     db.commit()
#
#     return {"answer": result["answer"], "sources": result["sources"], "response_time": result["response_time"]}
#
#
# @app.delete("/session/{session_id}")
# def clear_session(session_id: str, db: Session = Depends(get_db)):
#     db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
#     db.commit()
#     return {"message": "Session cleared"}
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)  ### yaha tak without docker hai

"""
FastAPI backend server for PDF RAG application.

This module provides REST API endpoints for PDF upload, document management,
chat sessions, and RAG-powered question answering.
"""

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field, validator
from typing import Optional, List
import shutil
import os
import uuid
from datetime import datetime
import logging

from db import init_db, get_db, Document, ChatSession, ChatMessage, QueryMetric
from pdf_processor import pdf_proc
from vector_db import vdb
from rag_engine import rag

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="PDF RAG API",
    description="REST API for PDF-based Retrieval-Augmented Generation",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Ensure uploads directory exists
os.makedirs("uploads", exist_ok=True)


@app.on_event("startup")
def startup():
    """Initialize database tables on application startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


# Pydantic models for request/response validation
class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    query: str = Field(..., min_length=1, description="User query text")
    session_id: str = Field(..., description="Chat session identifier")
    top_k: Optional[int] = Field(5, ge=1, le=20, description="Number of results to retrieve")
    doc_filter: Optional[int] = Field(None, description="Filter by document ID")
    only_if_sources: Optional[bool] = Field(False, description="Only answer if sources found")

    @validator('query')
    def query_not_empty(cls, v):
        """Validate query is not empty or whitespace."""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class SessionRequest(BaseModel):
    """Request model for session creation."""
    session_id: Optional[str] = Field(None, description="Optional session ID")


# API Endpoints

@app.get("/", tags=["Health"])
def root():
    """
    Root endpoint for health check.

    Returns:
        dict: API status and version
    """
    return {
        "status": "healthy",
        "service": "PDF RAG API",
        "version": "1.0.0"
    }


@app.post("/upload", tags=["Documents"], status_code=status.HTTP_201_CREATED)
async def upload_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Upload and process a PDF file.

    Accepts a PDF file, extracts text, chunks it, and indexes into vector database.
    Stores document metadata in PostgreSQL.

    Args:
        file (UploadFile): PDF file to upload
        db (Session): Database session

    Returns:
        dict: Document information including ID, filename, status, and page count

    Raises:
        HTTPException: If file is not PDF or processing fails
    """
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        logger.warning(f"Invalid file type attempted: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    file_path = None
    doc = None

    try:
        # Save uploaded file temporarily
        file_path = f"uploads/{uuid.uuid4()}_{file.filename}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        logger.info(f"Saved uploaded file: {file.filename}")

        # Create document record
        doc = Document(filename=file.filename, status="processing")
        db.add(doc)
        db.commit()
        db.refresh(doc)
        logger.info(f"Created document record with ID: {doc.id}")

        # Process PDF
        chunks, page_count = pdf_proc.process(file_path)
        logger.info(f"Extracted {len(chunks)} chunks from {page_count} pages")

        # Index chunks in vector database
        vdb.add_chunks(chunks, doc.id, file.filename)
        logger.info(f"Indexed {len(chunks)} chunks for document {doc.id}")

        # Update document status
        doc.status = "completed"
        doc.page_count = page_count
        db.commit()

        return {
            "id": doc.id,
            "filename": file.filename,
            "status": "completed",
            "page_count": page_count,
            "chunks": len(chunks)
        }

    except Exception as e:
        logger.error(f"Upload processing failed: {e}")

        # Update document status to failed if record exists
        if doc:
            try:
                doc.status = "failed"
                db.commit()
            except SQLAlchemyError:
                db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF: {str(e)}"
        )

    finally:
        # Clean up temporary file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up temporary file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to remove temporary file: {e}")


@app.get("/documents", tags=["Documents"])
def get_documents(db: Session = Depends(get_db)):
    """
    Retrieve all uploaded documents.

    Args:
        db (Session): Database session

    Returns:
        list: List of document metadata dictionaries
    """
    try:
        docs = db.query(Document).order_by(Document.upload_time.desc()).all()
        logger.info(f"Retrieved {len(docs)} documents")

        return [
            {
                "id": d.id,
                "filename": d.filename,
                "status": d.status,
                "page_count": d.page_count,
                "upload_time": d.upload_time
            }
            for d in docs
        ]
    except SQLAlchemyError as e:
        logger.error(f"Failed to retrieve documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )


@app.delete("/documents/{doc_id}", tags=["Documents"])
def delete_document(doc_id: int, db: Session = Depends(get_db)):
    """
    Delete a document and its vector embeddings.

    Args:
        doc_id (int): Document ID to delete
        db (Session): Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: If document not found or deletion fails
    """
    try:
        doc = db.query(Document).filter(Document.id == doc_id).first()

        if not doc:
            logger.warning(f"Document {doc_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Delete from vector database
        vdb.delete_doc(doc_id)
        logger.info(f"Deleted vector embeddings for document {doc_id}")

        # Delete from PostgreSQL
        db.delete(doc)
        db.commit()
        logger.info(f"Deleted document {doc_id} from database")

        return {"message": f"Document '{doc.filename}' deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document {doc_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


@app.post("/session", tags=["Sessions"], status_code=status.HTTP_201_CREATED)
def create_session(req: SessionRequest, db: Session = Depends(get_db)):
    """
    Create or retrieve a chat session.

    Args:
        req (SessionRequest): Session request with optional session_id
        db (Session): Database session

    Returns:
        dict: Session ID
    """
    try:
        sid = req.session_id or str(uuid.uuid4())

        existing = db.query(ChatSession).filter(ChatSession.session_id == sid).first()

        if not existing:
            session = ChatSession(session_id=sid)
            db.add(session)
            db.commit()
            logger.info(f"Created new session: {sid}")
        else:
            logger.info(f"Retrieved existing session: {sid}")

        return {"session_id": sid}

    except SQLAlchemyError as e:
        logger.error(f"Failed to create session: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )


@app.get("/sessions", tags=["Sessions"])
def get_sessions(db: Session = Depends(get_db)):
    """
    Retrieve all chat sessions.

    Args:
        db (Session): Database session

    Returns:
        list: List of session dictionaries
    """
    try:
        sessions = db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
        logger.info(f"Retrieved {len(sessions)} sessions")

        return [
            {
                "session_id": s.session_id,
                "created_at": s.created_at
            }
            for s in sessions
        ]
    except SQLAlchemyError as e:
        logger.error(f"Failed to retrieve sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )


@app.get("/messages/{session_id}", tags=["Sessions"])
def get_messages(session_id: str, db: Session = Depends(get_db)):
    """
    Retrieve chat messages for a session.

    Args:
        session_id (str): Session identifier
        db (Session): Database session

    Returns:
        list: List of message dictionaries
    """
    try:
        msgs = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp).all()

        logger.info(f"Retrieved {len(msgs)} messages for session {session_id}")

        return [
            {
                "role": m.role,
                "content": m.content,
                "sources": m.sources,
                "timestamp": m.timestamp
            }
            for m in msgs
        ]
    except SQLAlchemyError as e:
        logger.error(f"Failed to retrieve messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve messages"
        )


@app.post("/query", tags=["RAG"])
def query_rag(req: QueryRequest, db: Session = Depends(get_db)):
    """
    Process a RAG query and generate an answer.

    Stores user message, retrieves relevant context, generates answer using LLM,
    stores assistant response, and logs metrics.

    Args:
        req (QueryRequest): Query request with question and parameters
        db (Session): Database session

    Returns:
        dict: Answer, sources, and response time

    Raises:
        HTTPException: If query processing fails
    """
    try:
        # Store user message
        user_msg = ChatMessage(
            session_id=req.session_id,
            role="user",
            content=req.query
        )
        db.add(user_msg)
        db.commit()
        logger.info(f"Stored user message for session {req.session_id}")

        # Generate answer
        result = rag.generate_answer(
            req.query,
            req.top_k,
            req.doc_filter,
            req.only_if_sources
        )

        # Store assistant message
        assistant_msg = ChatMessage(
            session_id=req.session_id,
            role="assistant",
            content=result["answer"],
            sources=result["sources"]
        )
        db.add(assistant_msg)

        # Store metrics
        metric = QueryMetric(
            session_id=req.session_id,
            query=req.query,
            response_time=result["response_time"],
            retrieval_count=result["retrieval_count"]
        )
        db.add(metric)

        db.commit()
        logger.info(
            f"Query processed in {result['response_time']:.2f}s "
            f"with {result['retrieval_count']} sources"
        )

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "response_time": result["response_time"]
        }

    except ValueError as e:
        logger.warning(f"Invalid query: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error during query: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query"
        )
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process query: {str(e)}"
        )


@app.delete("/session/{session_id}", tags=["Sessions"])
def clear_session(session_id: str, db: Session = Depends(get_db)):
    """
    Clear all messages in a chat session.

    Args:
        session_id (str): Session identifier
        db (Session): Database session

    Returns:
        dict: Success message
    """
    try:
        deleted_count = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).delete()

        db.commit()
        logger.info(f"Cleared {deleted_count} messages from session {session_id}")

        return {"message": f"Session cleared ({deleted_count} messages deleted)"}

    except SQLAlchemyError as e:
        logger.error(f"Failed to clear session: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear session"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)