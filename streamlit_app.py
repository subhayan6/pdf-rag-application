# import streamlit as st
# import requests
# import uuid
# from datetime import datetime
# from dotenv import load_dotenv
# load_dotenv()
#
# API_URL = "http://localhost:8000"
#
# st.set_page_config(page_title="PDF RAG Chat", layout="wide")
#
# if "session_id" not in st.session_state:
#     st.session_state.session_id = str(uuid.uuid4())
#     requests.post(f"{API_URL}/session", json={"session_id": st.session_state.session_id})
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "documents" not in st.session_state:
#     st.session_state.documents = []
#
# st.title("📄 PDF RAG Chat")
#
# with st.sidebar:
#     st.header("📁 Documents")
#     uploaded = st.file_uploader("Upload PDF", type=["pdf"], key="uploader")
#     if uploaded and uploaded.name not in [d['filename'] for d in st.session_state.get('documents', [])]:
#         with st.spinner("Processing..."):
#             files = {"file": uploaded}
#             r = requests.post(f"{API_URL}/upload", files=files)
#             if r.status_code == 200:
#                 st.success(f"✅ {uploaded.name}")
#                 st.session_state.documents = requests.get(f"{API_URL}/documents").json()
#                 st.rerun()
#
#     docs = requests.get(f"{API_URL}/documents").json()
#     st.session_state.documents = docs
#     for d in docs:
#         with st.expander(f"📄 {d['filename']}"):
#             st.write(f"Status: {d['status']}")
#             st.write(f"Pages: {d['page_count']}")
#             if st.button("🗑️ Delete", key=f"del_{d['id']}"):
#                 requests.delete(f"{API_URL}/documents/{d['id']}")
#                 st.rerun()
#
#     st.divider()
#     st.header("⚙️ Settings")
#     top_k = st.slider("Top K", 1, 10, 5)
#     doc_filter = st.selectbox("Filter by doc", [None] + [d['id'] for d in docs])
#     only_sources = st.checkbox("Only answer if sources found", value=False)
#
#     st.divider()
#     if st.button("🗑️ Clear Chat"):
#         requests.delete(f"{API_URL}/session/{st.session_state.session_id}")
#         st.session_state.messages = []
#         st.rerun()
#
# col1, col2 = st.columns([3, 1])
# with col2:
#     sessions = requests.get(f"{API_URL}/sessions").json()
#     session_ids = [s['session_id'] for s in sessions]
#     if st.selectbox("Session", session_ids, index=session_ids.index(
#             st.session_state.session_id) if st.session_state.session_id in session_ids else 0,
#                     key="session_select") != st.session_state.session_id:
#         st.session_state.session_id = st.session_state.session_select
#         msgs = requests.get(f"{API_URL}/messages/{st.session_state.session_id}").json()
#         st.session_state.messages = msgs
#         st.rerun()
#
# with col1:
#     st.header("💬 Chat")
#     for msg in st.session_state.messages:
#         with st.chat_message(msg['role']):
#             st.write(msg['content'])
#             if msg['role'] == 'assistant' and msg.get('sources'):
#                 with st.expander("📚 Sources"):
#                     for s in msg['sources']:
#                         st.caption(f"**{s['filename']}** (Page {s['page']}) - Score: {s['score']:.3f}")
#                         st.text(s['text'][:200] + "...")
#
#     if query := st.chat_input("Ask about your PDFs..."):
#         st.session_state.messages.append({"role": "user", "content": query})
#         with st.chat_message("user"):
#             st.write(query)
#
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking..."):
#                 r = requests.post(f"{API_URL}/query",
#                                   json={"query": query, "session_id": st.session_state.session_id, "top_k": top_k,
#                                         "doc_filter": doc_filter, "only_if_sources": only_sources})
#                 data = r.json()
#                 st.write(data['answer'])
#                 if data['sources']:
#                     with st.expander("📚 Sources"):
#                         for s in data['sources']:
#                             st.caption(f"**{s['filename']}** (Page {s['page']}) - Score: {s['score']:.3f}")
#                             st.text(s['text'][:200] + "...")
#                 st.session_state.messages.append(
#                     {"role": "assistant", "content": data['answer'], "sources": data['sources']})

#yaha tak without docker hai

"""
Streamlit frontend application for PDF RAG system.

This module provides an interactive web interface for uploading PDFs,
managing documents, and chatting with document content using RAG.
"""

import streamlit as st
import requests
import uuid
import os
from datetime import datetime
from typing import Optional, List, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API URL - uses environment variable for Docker compatibility
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="PDF RAG Chat",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """
    Initialize Streamlit session state variables.

    Creates a new chat session if one doesn't exist and initializes
    messages and documents lists.
    """
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
        try:
            response = requests.post(
                f"{API_URL}/session",
                json={"session_id": st.session_state.session_id},
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"Created session: {st.session_state.session_id}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create session: {e}")
            st.error("Failed to connect to backend. Please check if the API is running.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "documents" not in st.session_state:
        st.session_state.documents = []


def fetch_documents() -> List[Dict]:
    """
    Fetch all documents from the API.

    Returns:
        List[Dict]: List of document dictionaries

    Raises:
        requests.exceptions.RequestException: If API request fails
    """
    try:
        response = requests.get(f"{API_URL}/documents", timeout=5)
        response.raise_for_status()
        docs = response.json()
        logger.info(f"Fetched {len(docs)} documents")
        return docs
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch documents: {e}")
        st.error("Failed to fetch documents from server")
        return []


def upload_document(uploaded_file) -> Optional[Dict]:
    """
    Upload a PDF file to the backend.

    Args:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        Optional[Dict]: Upload response data or None if failed
    """
    try:
        files = {"file": uploaded_file}
        response = requests.post(
            f"{API_URL}/upload",
            files=files,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Uploaded document: {uploaded_file.name}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Upload failed: {e}")
        st.error(f"Failed to upload document: {str(e)}")
        return None


def delete_document(doc_id: int) -> bool:
    """
    Delete a document from the backend.

    Args:
        doc_id (int): Document ID to delete

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        response = requests.delete(f"{API_URL}/documents/{doc_id}", timeout=5)
        response.raise_for_status()
        logger.info(f"Deleted document ID: {doc_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to delete document {doc_id}: {e}")
        st.error("Failed to delete document")
        return False


def send_query(query: str, top_k: int, doc_filter: Optional[int], only_sources: bool) -> Optional[Dict]:
    """
    Send a query to the RAG backend.

    Args:
        query (str): User's question
        top_k (int): Number of results to retrieve
        doc_filter (Optional[int]): Document ID filter
        only_sources (bool): Only answer if sources found

    Returns:
        Optional[Dict]: Response data or None if failed
    """
    try:
        payload = {
            "query": query,
            "session_id": st.session_state.session_id,
            "top_k": top_k,
            "doc_filter": doc_filter,
            "only_if_sources": only_sources
        }
        response = requests.post(
            f"{API_URL}/query",
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Query processed in {result.get('response_time', 0):.2f}s")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Query failed: {e}")
        st.error(f"Failed to process query: {str(e)}")
        return None


def clear_chat_session() -> bool:
    """
    Clear all messages in the current chat session.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        response = requests.delete(
            f"{API_URL}/session/{st.session_state.session_id}",
            timeout=5
        )
        response.raise_for_status()
        logger.info(f"Cleared session: {st.session_state.session_id}")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to clear session: {e}")
        st.error("Failed to clear chat")
        return False


def fetch_messages(session_id: str) -> List[Dict]:
    """
    Fetch chat messages for a session.

    Args:
        session_id (str): Session identifier

    Returns:
        List[Dict]: List of message dictionaries
    """
    try:
        response = requests.get(f"{API_URL}/messages/{session_id}", timeout=5)
        response.raise_for_status()
        messages = response.json()
        logger.info(f"Fetched {len(messages)} messages for session {session_id}")
        return messages
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch messages: {e}")
        return []


def fetch_sessions() -> List[Dict]:
    """
    Fetch all chat sessions.

    Returns:
        List[Dict]: List of session dictionaries
    """
    try:
        response = requests.get(f"{API_URL}/sessions", timeout=5)
        response.raise_for_status()
        sessions = response.json()
        return sessions
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch sessions: {e}")
        return []


def render_sidebar():
    """
    Render the sidebar with document management and settings.

    Returns:
        tuple: (top_k, doc_filter, only_sources) settings
    """
    with st.sidebar:
        st.header("📁 Documents")

        # File uploader
        uploaded = st.file_uploader("Upload PDF", type=["pdf"], key="uploader")

        if uploaded:
            # Check if already uploaded
            existing_files = [d['filename'] for d in st.session_state.get('documents', [])]

            if uploaded.name not in existing_files:
                with st.spinner(f"Processing {uploaded.name}..."):
                    result = upload_document(uploaded)

                    if result:
                        st.success(f"✅ {uploaded.name} ({result.get('page_count', 0)} pages)")
                        st.session_state.documents = fetch_documents()
                        st.rerun()
            else:
                st.info(f"📄 {uploaded.name} already uploaded")

        # Display documents
        docs = fetch_documents()
        st.session_state.documents = docs

        if not docs:
            st.info("No documents uploaded yet")

        for d in docs:
            with st.expander(f"📄 {d['filename']}"):
                st.write(f"**Status:** {d['status']}")
                st.write(f"**Pages:** {d.get('page_count', 'N/A')}")
                st.write(f"**Uploaded:** {d.get('upload_time', 'N/A')[:19]}")

                if st.button("🗑️ Delete", key=f"del_{d['id']}"):
                    if delete_document(d['id']):
                        st.success("Document deleted")
                        st.rerun()

        st.divider()

        # Settings
        st.header("⚙️ Settings")
        top_k = st.slider("Top K Results", 1, 10, 5, help="Number of document chunks to retrieve")

        doc_options = ["All Documents"] + [f"{d['filename']}" for d in docs]
        doc_selection = st.selectbox("Filter by Document", doc_options)
        doc_filter = None

        if doc_selection != "All Documents":
            # Find document ID
            for d in docs:
                if d['filename'] == doc_selection:
                    doc_filter = d['id']
                    break

        only_sources = st.checkbox(
            "Only answer if sources found",
            value=False,
            help="Return error if no relevant sources found"
        )

        st.divider()

        # Clear chat button
        if st.button("🗑️ Clear Chat", use_container_width=True):
            if clear_chat_session():
                st.session_state.messages = []
                st.success("Chat cleared")
                st.rerun()

        return top_k, doc_filter, only_sources


def render_chat_interface(top_k: int, doc_filter: Optional[int], only_sources: bool):
    """
    Render the main chat interface.

    Args:
        top_k (int): Number of results to retrieve
        doc_filter (Optional[int]): Document ID filter
        only_sources (bool): Only answer if sources found
    """
    col1, col2 = st.columns([3, 1])

    with col2:
        st.subheader("💬 Sessions")
        sessions = fetch_sessions()

        if sessions:
            session_ids = [s['session_id'] for s in sessions]
            session_labels = [
                f"{s['session_id'][:8]}... ({s.get('created_at', '')[:10]})"
                for s in sessions
            ]

            current_index = 0
            if st.session_state.session_id in session_ids:
                current_index = session_ids.index(st.session_state.session_id)

            selected_label = st.selectbox(
                "Select Session",
                session_labels,
                index=current_index,
                key="session_select"
            )

            selected_id = session_ids[session_labels.index(selected_label)]

            if selected_id != st.session_state.session_id:
                st.session_state.session_id = selected_id
                st.session_state.messages = fetch_messages(selected_id)
                st.rerun()

    with col1:
        st.header("💬 Chat")

        # Display chat messages
        for msg in st.session_state.messages:
            with st.chat_message(msg['role']):
                st.write(msg['content'])

                # Show sources for assistant messages
                if msg['role'] == 'assistant' and msg.get('sources'):
                    with st.expander(f"📚 Sources ({len(msg['sources'])})"):
                        for i, s in enumerate(msg['sources'], 1):
                            st.caption(
                                f"**{i}. {s['filename']}** (Page {s['page']}) "
                                f"- Relevance: {s['score']:.3f}"
                            )
                            st.text(s['text'][:200] + "..." if len(s['text']) > 200 else s['text'])
                            st.divider()

    # Chat input OUTSIDE columns - this is the fix!
    if query := st.chat_input("Ask about your PDFs..."):
        # Add user message to UI
        st.session_state.messages.append({"role": "user", "content": query})

        # Generate response
        with st.spinner("Thinking..."):
            response = send_query(query, top_k, doc_filter, only_sources)

            if response:
                # Add assistant message to state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response['answer'],
                    "sources": response.get('sources', [])
                })

                # Rerun to show the messages
                st.rerun()


def main():
    """Main application entry point."""
    st.title("📄 PDF RAG Chat")

    # Initialize session state
    init_session_state()

    # Render sidebar and get settings
    top_k, doc_filter, only_sources = render_sidebar()

    # Render main chat interface
    render_chat_interface(top_k, doc_filter, only_sources)


if __name__ == "__main__":
    main()