# import google.generativeai as genai
# from config import cfg
# from vector_db import vdb
# import time
#
# genai.configure(api_key=cfg.GEMINI_API_KEY)
#
#
# class RAGEngine:
#     def __init__(self):
#         self.model = genai.GenerativeModel('gemini-2.5-flash')
#
#     def generate_answer(self, query, top_k=5, doc_filter=None, only_if_sources=False):
#         start = time.time()
#         results = vdb.search(query, top_k, doc_filter)
#
#         if only_if_sources and not results:
#             return {"answer": "No relevant sources found for your query.", "sources": [],
#                     "response_time": time.time() - start, "retrieval_count": 0}
#
#         context = ""
#         for i, r in enumerate(results):
#             context += f"[Doc: {r['filename']}, Page: {r['page']}]\n{r['text']}\n\n"
#
#         prompt = f"""Answer the question based on the context below. Include citations with document name and page number.
#
# Context:
# {context}
#
# Question: {query}
#
# Answer with citations:"""
#
#         response = self.model.generate_content(prompt)
#         answer = response.text
#
#         return {
#             "answer": answer,
#             "sources": results,
#             "response_time": time.time() - start,
#             "retrieval_count": len(results)
#         }
#
#
# rag = RAGEngine()  ## yaha tak without docker hai
"""
RAG (Retrieval-Augmented Generation) engine module.

This module orchestrates the RAG pipeline by combining vector search results
with Google Gemini LLM to generate contextual answers with citations.
"""

import google.generativeai as genai
from typing import Dict, List, Optional
import time
import logging

from config import cfg
from vector_db import vdb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API
try:
    genai.configure(api_key=cfg.GEMINI_API_KEY)
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    raise


class RAGEngine:
    """
    Retrieval-Augmented Generation engine for question answering.

    Combines semantic search with LLM generation to answer questions based
    on document context. Provides source attribution and performance metrics.

    Attributes:
        model (GenerativeModel): Google Gemini generative model instance
    """

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initialize RAG engine with specified Gemini model.

        Args:
            model_name (str): Name of the Gemini model to use

        Raises:
            Exception: If model initialization fails
        """
        try:
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Initialized RAG engine with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise Exception(f"Model initialization failed: {str(e)}")

    def _build_context(self, results: List[Dict]) -> str:
        """
        Build context string from search results.

        Formats retrieved chunks into a structured context for the LLM,
        including document name and page number for each chunk.

        Args:
            results (List[Dict]): Search results from vector database

        Returns:
            str: Formatted context string
        """
        if not results:
            return "No relevant context found."

        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"[Source {i} - Doc: {r['filename']}, Page: {r['page']}]\n{r['text']}\n"
            )

        return "\n".join(context_parts)

    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build the prompt for the LLM.

        Creates a structured prompt that instructs the model to answer
        based on provided context with proper citations.

        Args:
            query (str): User's question
            context (str): Retrieved context from documents

        Returns:
            str: Complete prompt for the LLM
        """
        prompt = f"""You are a helpful AI assistant that answers questions based on the provided context from PDF documents.

Instructions:
1. Answer the question using ONLY information from the context below
2. Include citations with document name and page number in your answer
3. If the context doesn't contain relevant information, say so clearly
4. Be concise but comprehensive
5. Format citations as: (Document Name, Page X)

Context:
{context}

Question: {query}

Answer with citations:"""

        return prompt

    def generate_answer(
            self,
            query: str,
            top_k: int = 5,
            doc_filter: Optional[int] = None,
            only_if_sources: bool = False
    ) -> Dict:
        """
        Generate an answer to a query using RAG pipeline.

        Retrieves relevant document chunks and uses Gemini to generate
        a contextual answer with citations. Tracks performance metrics.

        Args:
            query (str): User's question
            top_k (int): Number of chunks to retrieve (default: 5)
            doc_filter (int, optional): Filter results by document ID
            only_if_sources (bool): Return error if no sources found (default: False)

        Returns:
            Dict: Response containing:
                - answer (str): Generated answer text
                - sources (List[Dict]): Retrieved source chunks
                - response_time (float): Total processing time in seconds
                - retrieval_count (int): Number of chunks retrieved

        Raises:
            ValueError: If query is empty
            Exception: If generation fails

        Example:
            response = rag.generate_answer("What is machine learning?", top_k=3)
            print(response['answer'])
            print(f"Found {response['retrieval_count']} sources")
        """
        if not query or not query.strip():
            logger.warning("Empty query received")
            raise ValueError("Query cannot be empty")

        start_time = time.time()

        try:
            # Retrieve relevant chunks
            logger.info(f"Searching for query: '{query[:50]}...' with top_k={top_k}")
            results = vdb.search(query, top_k, doc_filter)

            # Handle no results case
            if only_if_sources and not results:
                response_time = time.time() - start_time
                logger.info("No sources found and only_if_sources=True")
                return {
                    "answer": "No relevant sources found for your query. Please try rephrasing or check if documents are uploaded.",
                    "sources": [],
                    "response_time": response_time,
                    "retrieval_count": 0
                }

            # Build context and prompt
            context = self._build_context(results)
            prompt = self._build_prompt(query, context)

            # Generate answer using Gemini
            logger.info(f"Generating answer with {len(results)} sources")
            response = self.model.generate_content(prompt)
            answer = response.text

            response_time = time.time() - start_time

            logger.info(
                f"Generated answer in {response_time:.2f}s with {len(results)} sources"
            )

            return {
                "answer": answer,
                "sources": results,
                "response_time": response_time,
                "retrieval_count": len(results)
            }

        except ValueError as e:
            logger.error(f"Validation error: {e}")
            raise
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Answer generation failed after {response_time:.2f}s: {e}")

            # Return graceful error response
            return {
                "answer": f"I encountered an error while generating the answer: {str(e)}. Please try again.",
                "sources": [],
                "response_time": response_time,
                "retrieval_count": 0
            }


# Global RAG engine instance
rag = RAGEngine()

