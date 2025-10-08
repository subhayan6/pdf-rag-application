# import fitz
# from config import cfg
#
#
# class PDFProcessor:
#     def __init__(self):
#         self.chunk_size = cfg.CHUNK_SIZE
#         self.overlap = cfg.CHUNK_OVERLAP
#
#     def extract_text(self, pdf_path):
#         doc = fitz.open(pdf_path)
#         pages = []
#         for i, page in enumerate(doc):
#             pages.append({"page": i + 1, "text": page.get_text()})
#         doc.close()
#         return pages, len(pages)
#
#     def chunk_text(self, pages):
#         chunks = []
#         for page_data in pages:
#             text = page_data["text"]
#             page_num = page_data["page"]
#             if not text.strip():
#                 continue
#             words = text.split()
#             for i in range(0, len(words), self.chunk_size - self.overlap):
#                 chunk = " ".join(words[i:i + self.chunk_size])
#                 if chunk.strip():
#                     chunks.append({"text": chunk, "page": page_num})
#         return chunks
#
#     def process(self, pdf_path):
#         pages, page_count = self.extract_text(pdf_path)
#         chunks = self.chunk_text(pages)
#         return chunks, page_count
#
#
# pdf_proc = PDFProcessor() ### yaha tak without docker hai

"""
PDF processing module for text extraction and chunking.

This module handles PDF text extraction using PyMuPDF (fitz) and implements
a word-based chunking strategy with configurable overlap for optimal RAG
performance.
"""

import fitz
from typing import List, Dict, Tuple
import logging
from pathlib import Path

from config import cfg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    PDF processor for extracting and chunking text from PDF documents.

    Uses PyMuPDF (fitz) for fast and accurate text extraction. Implements
    word-based chunking with overlap to maintain context across chunks.

    Attributes:
        chunk_size (int): Number of words per chunk
        overlap (int): Number of overlapping words between consecutive chunks
    """

    def __init__(self, chunk_size: int = None, overlap: int = None):
        """
        Initialize PDF processor with chunking parameters.

        Args:
            chunk_size (int, optional): Words per chunk. Defaults to config value.
            overlap (int, optional): Overlapping words. Defaults to config value.

        Raises:
            ValueError: If overlap >= chunk_size
        """
        self.chunk_size = chunk_size or cfg.CHUNK_SIZE
        self.overlap = overlap or cfg.CHUNK_OVERLAP

        if self.overlap >= self.chunk_size:
            raise ValueError(
                f"Overlap ({self.overlap}) must be less than chunk_size ({self.chunk_size})"
            )

        logger.info(f"PDFProcessor initialized: chunk_size={self.chunk_size}, overlap={self.overlap}")

    def extract_text(self, pdf_path: str) -> Tuple[List[Dict[str, any]], int]:
        """
        Extract text from PDF file page by page.

        Args:
            pdf_path (str): Path to the PDF file

        Returns:
            Tuple[List[Dict], int]: List of page dictionaries with text and page numbers,
                                   and total page count

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF cannot be opened or read

        Example:
            pages, count = processor.extract_text("document.pdf")
            # pages = [{"page": 1, "text": "..."}, {"page": 2, "text": "..."}]
        """
        # Validate file exists
        if not Path(pdf_path).exists():
            logger.error(f"PDF file not found: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)
            pages = []

            for i, page in enumerate(doc):
                try:
                    text = page.get_text()
                    pages.append({"page": i + 1, "text": text})
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {i + 1}: {e}")
                    pages.append({"page": i + 1, "text": ""})

            page_count = len(doc)
            doc.close()

            logger.info(f"Extracted text from {page_count} pages in {pdf_path}")
            return pages, page_count

        except Exception as e:
            logger.error(f"Failed to open PDF {pdf_path}: {e}")
            raise Exception(f"Failed to process PDF: {str(e)}")

    def chunk_text(self, pages: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Chunk extracted text using word-based sliding window with overlap.

        Splits text into overlapping chunks to maintain context. Empty pages
        and chunks are filtered out.

        Args:
            pages (List[Dict]): List of page dictionaries from extract_text()

        Returns:
            List[Dict]: List of chunk dictionaries with text, page number

        Example:
            chunks = processor.chunk_text(pages)
            # chunks = [{"text": "...", "page": 1}, {"text": "...", "page": 1}, ...]
        """
        chunks = []

        for page_data in pages:
            text = page_data["text"]
            page_num = page_data["page"]

            # Skip empty pages
            if not text.strip():
                logger.debug(f"Skipping empty page {page_num}")
                continue

            # Split into words
            words = text.split()

            # Create overlapping chunks
            for i in range(0, len(words), self.chunk_size - self.overlap):
                chunk_words = words[i:i + self.chunk_size]
                chunk_text = " ".join(chunk_words)

                # Only add non-empty chunks
                if chunk_text.strip():
                    chunks.append({
                        "text": chunk_text,
                        "page": page_num
                    })

        logger.info(f"Created {len(chunks)} chunks from {len(pages)} pages")
        return chunks

    def process(self, pdf_path: str) -> Tuple[List[Dict[str, any]], int]:
        """
        Complete PDF processing pipeline: extract and chunk text.

        Convenience method that combines extract_text() and chunk_text()
        into a single operation.

        Args:
            pdf_path (str): Path to the PDF file

        Returns:
            Tuple[List[Dict], int]: List of text chunks and page count

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If processing fails

        Example:
            chunks, page_count = processor.process("document.pdf")
        """
        try:
            pages, page_count = self.extract_text(pdf_path)
            chunks = self.chunk_text(pages)

            logger.info(f"Successfully processed {pdf_path}: {len(chunks)} chunks from {page_count} pages")
            return chunks, page_count

        except Exception as e:
            logger.error(f"PDF processing failed for {pdf_path}: {e}")
            raise


# Global processor instance
pdf_proc = PDFProcessor()