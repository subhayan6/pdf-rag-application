# from qdrant_client import QdrantClient
# from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
# from sentence_transformers import SentenceTransformer
# from config import cfg
# import uuid
#
#
# class VectorDB:
#     def __init__(self):
#         self.client = QdrantClient(host=cfg.QDRANT_HOST, port=cfg.QDRANT_PORT)
#         self.model = SentenceTransformer(cfg.EMBEDDING_MODEL)
#         self.collection = "pdf_chunks"
#         self._init_collection()
#
#     def _init_collection(self):
#         collections = [c.name for c in self.client.get_collections().collections]
#         if self.collection not in collections:
#             self.client.create_collection(
#                 collection_name=self.collection,
#                 vectors_config=VectorParams(size=self.model.get_sentence_embedding_dimension(),
#                                             distance=Distance.COSINE)
#             )
#
#     def add_chunks(self, chunks, doc_id, filename):
#         points = []
#         for i, chunk in enumerate(chunks):
#             vec = self.model.encode(chunk["text"]).tolist()
#             points.append(PointStruct(
#                 id=str(uuid.uuid4()),
#                 vector=vec,
#                 payload={"text": chunk["text"], "page": chunk["page"], "doc_id": doc_id, "filename": filename,
#                          "chunk_id": i}
#             ))
#         self.client.upsert(collection_name=self.collection, points=points)
#         return len(points)
#
#     def search(self, query, top_k=5, doc_filter=None):
#         vec = self.model.encode(query).tolist()
#         filter_obj = None
#         if doc_filter:
#             filter_obj = Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_filter))])
#         results = self.client.search(collection_name=self.collection, query_vector=vec, limit=top_k,
#                                      query_filter=filter_obj)
#         return [
#             {"text": r.payload["text"], "page": r.payload["page"], "filename": r.payload["filename"], "score": r.score}
#             for r in results]
#
#     def delete_doc(self, doc_id):
#         self.client.delete(collection_name=self.collection,
#                            points_selector=Filter(must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]))
#
#
# vdb = VectorDB() ## yaha tak without docker hai

"""
Vector database module for semantic search using Qdrant.

This module provides vector storage and similarity search functionality using
Qdrant as the vector database and sentence-transformers for generating embeddings.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import uuid
import logging

from config import cfg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDB:
    """
    Vector database manager for semantic search operations.

    Manages Qdrant vector database connection, embedding generation using
    sentence-transformers, and provides methods for indexing and searching
    document chunks.

    Attributes:
        client (QdrantClient): Qdrant database client
        model (SentenceTransformer): Embedding model for text vectorization
        collection (str): Name of the Qdrant collection
    """

    def __init__(self, collection_name: str = "pdf_chunks"):
        """
        Initialize vector database connection and embedding model.

        Args:
            collection_name (str): Name of the Qdrant collection to use

        Raises:
            Exception: If connection to Qdrant fails
            Exception: If embedding model cannot be loaded
        """
        try:
            self.client = QdrantClient(host=cfg.QDRANT_HOST, port=cfg.QDRANT_PORT)
            logger.info(f"Connected to Qdrant at {cfg.QDRANT_HOST}:{cfg.QDRANT_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise Exception(f"Qdrant connection failed: {str(e)}")

        try:
            self.model = SentenceTransformer(cfg.EMBEDDING_MODEL)
            logger.info(f"Loaded embedding model: {cfg.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise Exception(f"Embedding model loading failed: {str(e)}")

        self.collection = collection_name
        self._init_collection()

    def _init_collection(self) -> None:
        """
        Initialize Qdrant collection if it doesn't exist.

        Creates a new collection with appropriate vector configuration
        based on the embedding model's dimension.

        Raises:
            Exception: If collection creation fails
        """
        try:
            collections = [c.name for c in self.client.get_collections().collections]

            if self.collection not in collections:
                vector_size = self.model.get_sentence_embedding_dimension()
                self.client.create_collection(
                    collection_name=self.collection,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection '{self.collection}' with vector size {vector_size}")
            else:
                logger.info(f"Collection '{self.collection}' already exists")

        except Exception as e:
            logger.error(f"Failed to initialize collection: {e}")
            raise Exception(f"Collection initialization failed: {str(e)}")

    def add_chunks(self, chunks: List[Dict], doc_id: int, filename: str) -> int:
        """
        Add document chunks to the vector database.

        Embeds each chunk and stores it in Qdrant with metadata including
        document ID, filename, page number, and chunk ID.

        Args:
            chunks (List[Dict]): List of chunk dictionaries with 'text' and 'page' keys
            doc_id (int): Database ID of the source document
            filename (str): Name of the source document

        Returns:
            int: Number of chunks successfully added

        Raises:
            ValueError: If chunks list is empty
            Exception: If embedding or insertion fails

        Example:
            chunks = [{"text": "...", "page": 1}, {"text": "...", "page": 2}]
            count = vdb.add_chunks(chunks, doc_id=1, filename="doc.pdf")
        """
        if not chunks:
            logger.warning(f"No chunks to add for document {doc_id}")
            raise ValueError("Chunks list cannot be empty")

        try:
            points = []
            for i, chunk in enumerate(chunks):
                # Generate embedding
                vec = self.model.encode(chunk["text"]).tolist()

                # Create point with metadata
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vec,
                    payload={
                        "text": chunk["text"],
                        "page": chunk["page"],
                        "doc_id": doc_id,
                        "filename": filename,
                        "chunk_id": i
                    }
                )
                points.append(point)

            # Batch upsert
            self.client.upsert(collection_name=self.collection, points=points)
            logger.info(f"Added {len(points)} chunks for document {doc_id} ({filename})")

            return len(points)

        except Exception as e:
            logger.error(f"Failed to add chunks for document {doc_id}: {e}")
            raise Exception(f"Chunk insertion failed: {str(e)}")

    def search(self, query: str, top_k: int = 5, doc_filter: Optional[int] = None) -> List[Dict]:
        """
        Search for similar chunks using semantic similarity.

        Embeds the query and retrieves the most similar chunks from the
        vector database. Optionally filters results by document ID.

        Args:
            query (str): Search query text
            top_k (int): Number of results to return (default: 5)
            doc_filter (int, optional): Filter results by document ID

        Returns:
            List[Dict]: List of matching chunks with text, page, filename, and score

        Raises:
            ValueError: If query is empty or top_k is invalid
            Exception: If search operation fails

        Example:
            results = vdb.search("What is machine learning?", top_k=3)
            # results = [{"text": "...", "page": 1, "filename": "...", "score": 0.85}, ...]
        """
        if not query or not query.strip():
            logger.warning("Empty query provided")
            raise ValueError("Query cannot be empty")

        if top_k < 1:
            logger.warning(f"Invalid top_k value: {top_k}")
            raise ValueError("top_k must be at least 1")

        try:
            # Generate query embedding
            vec = self.model.encode(query).tolist()

            # Build filter if document filter is specified
            filter_obj = None
            if doc_filter is not None:
                filter_obj = Filter(
                    must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_filter))]
                )

            # Perform search
            results = self.client.search(
                collection_name=self.collection,
                query_vector=vec,
                limit=top_k,
                query_filter=filter_obj
            )

            # Format results
            formatted_results = [
                {
                    "text": r.payload["text"],
                    "page": r.payload["page"],
                    "filename": r.payload["filename"],
                    "score": r.score
                }
                for r in results
            ]

            logger.info(f"Search returned {len(formatted_results)} results for query: '{query[:50]}...'")
            return formatted_results

        except UnexpectedResponse as e:
            logger.error(f"Qdrant search error: {e}")
            raise Exception(f"Search operation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise Exception(f"Search operation failed: {str(e)}")

    def delete_doc(self, doc_id: int) -> None:
        """
        Delete all chunks associated with a document.

        Removes all vector points that belong to the specified document ID.

        Args:
            doc_id (int): Database ID of the document to delete

        Raises:
            Exception: If deletion fails

        Example:
            vdb.delete_doc(doc_id=1)
        """
        try:
            self.client.delete(
                collection_name=self.collection,
                points_selector=Filter(
                    must=[FieldCondition(key="doc_id", match=MatchValue(value=doc_id))]
                )
            )
            logger.info(f"Deleted all chunks for document {doc_id}")

        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            raise Exception(f"Document deletion failed: {str(e)}")


# Global vector database instance
vdb = VectorDB()