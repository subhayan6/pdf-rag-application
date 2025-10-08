# from sqlalchemy import create_engine,Column,Integer,String,Text,DateTime,Float,JSON
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from datetime import datetime
# from config import cfg
#
# Base=declarative_base()
#
# class Document(Base):
#     __tablename__="documents"
#     id=Column(Integer,primary_key=True)
#     filename=Column(String(255),nullable=False)
#     upload_time=Column(DateTime,default=datetime.utcnow)
#     status=Column(String(50),default="processing")
#     page_count=Column(Integer)
#     meta=Column(JSON)
#
# class ChatSession(Base):
#     __tablename__="chat_sessions"
#     id=Column(Integer,primary_key=True)
#     session_id=Column(String(100),unique=True,nullable=False)
#     created_at=Column(DateTime,default=datetime.utcnow)
#     meta=Column(JSON)
#
# class ChatMessage(Base):
#     __tablename__="chat_messages"
#     id=Column(Integer,primary_key=True)
#     session_id=Column(String(100),nullable=False)
#     role=Column(String(20),nullable=False)
#     content=Column(Text,nullable=False)
#     timestamp=Column(DateTime,default=datetime.utcnow)
#     sources=Column(JSON)
#     meta=Column(JSON)
#
# class QueryMetric(Base):
#     __tablename__="query_metrics"
#     id=Column(Integer,primary_key=True)
#     session_id=Column(String(100))
#     query=Column(Text)
#     response_time=Column(Float)
#     retrieval_count=Column(Integer)
#     llm_tokens=Column(Integer)
#     timestamp=Column(DateTime,default=datetime.utcnow)
#     meta=Column(JSON)
#
# engine=create_engine(cfg.db_url)
# SessionLocal=sessionmaker(bind=engine)
#
# def init_db():
#     Base.metadata.create_all(engine)
#
# def get_db():
#     db=SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close() ### yaha tak without docker hai

"""
Database models and connection management for PDF RAG application.

This module defines SQLAlchemy ORM models for documents, chat sessions,
messages, and query metrics. It also provides database initialization
and session management utilities.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import Generator
import logging

from config import cfg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class Document(Base):
    """
    Document model representing uploaded PDF files.

    Attributes:
        id (int): Primary key
        filename (str): Original filename of the uploaded PDF
        upload_time (datetime): Timestamp of upload
        status (str): Processing status (processing, completed, failed)
        page_count (int): Number of pages in the PDF
        meta (dict): Additional metadata as JSON
    """
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="processing")
    page_count = Column(Integer)
    meta = Column(JSON)


class ChatSession(Base):
    """
    Chat session model for tracking user conversations.

    Attributes:
        id (int): Primary key
        session_id (str): Unique session identifier (UUID)
        created_at (datetime): Session creation timestamp
        meta (dict): Additional metadata as JSON
    """
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    meta = Column(JSON)


class ChatMessage(Base):
    """
    Chat message model for storing conversation history.

    Attributes:
        id (int): Primary key
        session_id (str): Associated session identifier
        role (str): Message role (user or assistant)
        content (str): Message text content
        timestamp (datetime): Message timestamp
        sources (dict): Retrieved sources for assistant responses
        meta (dict): Additional metadata as JSON
    """
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    sources = Column(JSON)
    meta = Column(JSON)


class QueryMetric(Base):
    """
    Query metrics model for tracking RAG performance.

    Attributes:
        id (int): Primary key
        session_id (str): Associated session identifier
        query (str): User query text
        response_time (float): Time taken to generate response (seconds)
        retrieval_count (int): Number of documents retrieved
        llm_tokens (int): Number of tokens used by LLM
        timestamp (datetime): Query timestamp
        meta (dict): Additional metadata as JSON
    """
    __tablename__ = "query_metrics"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100))
    query = Column(Text)
    response_time = Column(Float)
    retrieval_count = Column(Integer)
    llm_tokens = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    meta = Column(JSON)


# Create database engine
try:
    engine = create_engine(cfg.db_url, pool_pre_ping=True, pool_size=10, max_overflow=20)
    SessionLocal = sessionmaker(bind=engine)
    logger.info("Database engine created successfully")
except SQLAlchemyError as e:
    logger.error(f"Failed to create database engine: {e}")
    raise


def init_db() -> None:
    """
    Initialize database by creating all tables.

    Creates all tables defined by SQLAlchemy models if they don't exist.
    Should be called on application startup.

    Raises:
        SQLAlchemyError: If table creation fails
    """
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise


def get_db() -> Generator:
    """
    Dependency function for FastAPI to get database sessions.

    Provides a database session with automatic cleanup. Use with
    FastAPI's Depends() for dependency injection.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()