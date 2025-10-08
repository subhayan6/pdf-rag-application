# import os
# from dotenv import load_dotenv
#
# load_dotenv()
# class Config:
#     GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#     POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
#     POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
#     POSTGRES_DB = os.getenv("POSTGRES_DB", "claude_rag_db")
#     POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
#     POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
#     QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
#     QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
#     EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
#     CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))
#     CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
#     TOP_K = int(os.getenv("TOP_K", 5))
#
#     @property
#     def db_url(self):
#         return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
#
#
# cfg = Config()  # yaha tak without docker hai

"""
Configuration module for PDF RAG application.

This module loads environment variables and provides a centralized configuration
object for all application settings including database connections, API keys,
and embedding parameters.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Configuration class that holds all application settings.

    Loads settings from environment variables with sensible defaults.
    Validates critical settings on initialization.

    Attributes:
        GEMINI_API_KEY (str): API key for Google Gemini LLM
        POSTGRES_HOST (str): PostgreSQL database host
        POSTGRES_PORT (int): PostgreSQL database port
        POSTGRES_DB (str): PostgreSQL database name
        POSTGRES_USER (str): PostgreSQL username
        POSTGRES_PASSWORD (str): PostgreSQL password
        QDRANT_HOST (str): Qdrant vector database host
        QDRANT_PORT (int): Qdrant vector database port
        EMBEDDING_MODEL (str): Sentence transformer model name
        CHUNK_SIZE (int): Number of words per text chunk
        CHUNK_OVERLAP (int): Number of overlapping words between chunks
        TOP_K (int): Default number of results to retrieve
    """

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_DB = os.getenv("POSTGRES_DB", "claude_rag_db")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 512))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
    TOP_K = int(os.getenv("TOP_K", 5))

    def __init__(self):
        """
        Initialize configuration and validate critical settings.

        Raises:
            ValueError: If GEMINI_API_KEY is not set
        """
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is required. Please set it in your .env file or environment variables."
            )

        if self.CHUNK_OVERLAP >= self.CHUNK_SIZE:
            raise ValueError(
                f"CHUNK_OVERLAP ({self.CHUNK_OVERLAP}) must be less than CHUNK_SIZE ({self.CHUNK_SIZE})"
            )

    @property
    def db_url(self) -> str:
        """
        Construct PostgreSQL connection URL.

        Returns:
            str: SQLAlchemy-compatible database URL
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


# Global configuration instance
try:
    cfg = Config()
except ValueError as e:
    print(f"Configuration Error: {e}")
    raise