"""
Z.M.ai - Simple Academic Policy Assistant

A simplified RAG chatbot that:
1. Scrapes web content and stores it locally
2. Uses keyword-based retrieval for better results
3. Clean, simple single-file architecture
"""

import os
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional

import streamlit as st
import pdfplumber
import requests
from bs4 import BeautifulSoup
from groq import Groq

# -------------------- CONFIGURATION --------------------
PDF_PATH = "reference/Academic-Policy-Manual-for-Students2.pdf"
SCRAPE_URL = "https://iqra.edu.pk/iu-policies/"
LOCAL_CACHE = "data/policy_content.txt"
MODEL_NAME = "llama-3.1-8b-instant"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------- CSS STYLES --------------------
def inject_custom_css():
    """Inject professional CSS styles."""
    st.markdown("""
    <style>
        /* Main container */
        .stApp {
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%);
            background-attachment: fixed;
        }

        /* Chat messages */
        .stChatMessage {
            background-color: transparent;
        }

        /* User message */
        .stChatMessage[data-testid="stChatMessage:user"] {
            background: linear-gradient(135deg, #4f46e5, #8b5cf6);
            border-radius: 20px 20px 4px 20px;
            padding: 14px 20px !important;
        }

        /* Assistant message */
        .stChatMessage[data-testid="stChatMessage:assistant"] {
            background: white;
            border-radius: 20px 20px 20px 4px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            padding: 14px 20px !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 8px 20px rgba(0, 0, 0, 0.06);
        }

        /* Input area */
        .stChatInputContainer {
            border-top: 1px solid rgba(148, 163, 184, 0.2) !important;
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(24px);
        }

        .stChatInputContainer textarea {
            background: #f8fafc !important;
            border: 1px solid rgba(148, 163, 184, 0.2) !important;
            border-radius: 14px !important;
        }

        .stChatInputContainer textarea:focus {
            border-color: #4f46e5 !important;
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
        }
    </style>
    """, unsafe_allow_html=True)

# -------------------- DATA LOADING --------------------
def load_pdf_content(path: str) -> str:
    """Extract text from PDF file."""
    if not os.path.exists(path):
        logger.warning(f"PDF not found: {path}")
        return ""

    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- PDF Page {i} ---\n{page_text}\n"
        logger.info(f"Loaded PDF: {len(text)} characters")
    except Exception as e:
        logger.error(f"Error loading PDF: {e}")
    return text


def scrape_web_content(url: str) -> str:
    """Scrape content from website."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        # Get main content
        text = soup.get_text(separator="\n", strip=True)

        # Clean up
        lines = [line.strip() for line in text.split("\n") if line.strip() and len(line.strip()) > 3]
        text = "\n".join(lines)

        logger.info(f"Scraped web content: {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Error scraping web: {e}")
        return ""


def load_or_create_knowledge_base() -> str:
    """Load from cache or scrape and create knowledge base."""
    cache_dir = Path("data")
    cache_dir.mkdir(exist_ok=True)
    cache_file = Path(LOCAL_CACHE)

    # Try to load from cache
    if cache_file.exists():
        logger.info("Loading from local cache...")
        with open(cache_file, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info(f"Loaded from cache: {len(content)} characters")
        return content

    # Create new knowledge base
    logger.info("Creating knowledge base...")
    content = ""

    # Load PDF
    pdf_content = load_pdf_content(PDF_PATH)
    if pdf_content:
        content += f"\n{'='*60}\nPDF CONTENT\n{'='*60}\n{pdf_content}\n"

    # Scrape web
    web_content = scrape_web_content(SCRAPE_URL)
    if web_content:
        content += f"\n{'='*60}\nWEB CONTENT\n{'='*60}\n{web_content}\n"

    # Save to cache
    if content:
        with open(cache_file, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("Knowledge base saved to cache")

    return content


# -------------------- RETRIEVAL --------------------
def retrieve_context(query: str, knowledge_base: str, max_chunks: int = 5) -> str:
    """
    Retrieve relevant context using keyword matching.
    Better than embeddings for simple queries.
    """
    if not knowledge_base:
        return ""

    # Extract meaningful query words
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
    query_words.discard("what")
    query_words.discard("how")
    query_words.discard("is")
    query_words.discard("the")
    query_words.discard("a")
    query_words.discard("an")
    query_words.discard("are")
    query_words.discard("you")

    if not query_words:
        return ""

    # Split into chunks and score
    chunks = knowledge_base.split("\n\n")
    scored_chunks = []

    for chunk in chunks:
        if len(chunk.strip()) < 20:
            continue

        chunk_lower = chunk.lower()
        score = 0

        # Exact phrase matches (highest weight)
        for phrase in query_words:
            if phrase in chunk_lower:
                score += 3

        # Partial matches
        for word in query_words:
            if word in chunk_lower:
                score += 1

        # Check for related terms
        if "attendance" in query_words:
            if "present" in chunk_lower or "absent" in chunk_lower:
                score += 2
        if "grade" in query_words:
            if "gpa" in chunk_lower or "cgpa" in chunk_lower or "mark" in chunk_lower:
                score += 2
        if "exam" in query_words:
            if "test" in chunk_lower or "quiz" in chunk_lower or "assessment" in chunk_lower:
                score += 2

        if score > 0:
            scored_chunks.append((score, chunk))

    # Sort by score and get top chunks
    scored_chunks.sort(reverse=True, key=lambda x: x[0])

    if scored_chunks:
        top_chunks = [chunk for score, chunk in scored_chunks[:max_chunks]]
        context = "\n\n---\n\n".join(top_chunks)
        logger.info(f"Retrieved {len(top_chunks)} chunks for query (best score: {scored_chunks[0][0]})")
        return context

    return ""


# -------------------- LLM --------------------
def get_llm_response(query: str, context: str, history: List[dict]) -> str:
    """Get response from Groq LLM."""
    api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    if not api_key:
        return "⚠️ API Key missing. Please add GROQ_API_KEY to secrets."

    client = Groq(api_key=api_key)

    today = datetime.now().strftime("%d %B %Y")

    system_prompt = f"""You are Z.M.ai, a helpful academic policy assistant for university students.

Current Date: {today}

REFERENCE MATERIAL:
{context if context else ""}

INSTRUCTIONS:
1. Use the reference material above to provide accurate answers
2. Be professional, clear, and concise
3. Use bullet points or numbered lists for clarity
4. Keep answers relevant to academic policies
5. Answer helpfully based on what you know

Respond in a friendly, helpful manner."""

    # Build message history
    messages = [{"role": "system", "content": system_prompt}]

    # Add recent history (last 6 messages)
    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current query
    messages.append({"role": "user", "content": query})

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,
            max_tokens=2048
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM error: {e}")
        return f"⚠️ Error generating response: {str(e)}"


# -------------------- MAIN APP --------------------
def main():
    """Main application."""
    # Page config
    st.set_page_config(
        page_title="Z.M.ai | Academic Policy Assistant",
        page_icon="🧠",
        layout="centered"
    )

    # Inject CSS
    inject_custom_css()

    # Header
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 20px;">
        <div style="
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #4f46e5, #8b5cf6);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2);
        ">🧠</div>
        <div>
            <div style="font-size: 24px; font-weight: 700; color: #0f172a; letter-spacing: -0.03em;">Z.M.ai</div>
            <div style="font-size: 13px; color: #94a3b8; font-weight: 500; margin-top: 2px;">RAG-based Academic Policy Assistant</div>
            <div style="font-size: 11px; color: #cbd5e1; font-weight: 400; margin-top: 4px;">Built by Zayan & Maviya</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.knowledge_loaded = False

    # Load knowledge base (once per session)
    if not st.session_state.knowledge_loaded:
        with st.spinner("📚 Loading knowledge base..."):
            st.session_state.knowledge_base = load_or_create_knowledge_base()
            st.session_state.knowledge_loaded = True

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask about academic policies..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Retrieve context
                context = retrieve_context(prompt, st.session_state.knowledge_base)

                # Get LLM response
                response = get_llm_response(prompt, context, st.session_state.messages[:-1])

            st.markdown(response)

        # Add assistant message to history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Limit history
        if len(st.session_state.messages) > 100:
            st.session_state.messages = st.session_state.messages[-100:]

    # Footer
    st.markdown("""
    <div style="
        text-align: center;
        padding: 24px;
        color: #94a3b8;
        font-size: 12px;
        border-top: 1px solid rgba(148, 163, 184, 0.2);
        margin-top: 40px;
    ">
        Z.M.ai • A RAG-based LLM Chatbot built by Zayan & Maviya
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
