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

        /* Portfolio styles */
        .portfolio-header {
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #4f46e5, #8b5cf6);
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(79, 70, 229, 0.3);
        }
        .portfolio-section {
            background: white;
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        }
        .feature-card {
            background: linear-gradient(135deg, #f8fafc, #f1f5f9);
            padding: 20px;
            border-radius: 16px;
            border: 1px solid #e2e8f0;
            text-align: center;
        }
        .tech-badge {
            display: inline-block;
            background: linear-gradient(135deg, #4f46e5, #8b5cf6);
            color: white;
            padding: 8px 16px;
            border-radius: 100px;
            font-size: 14px;
            font-weight: 500;
            margin: 4px;
        }
        .link-button {
            display: inline-block;
            background: linear-gradient(135deg, #4f46e5, #8b5cf6);
            color: white;
            padding: 12px 30px;
            border-radius: 100px;
            text-decoration: none;
            font-weight: 600;
            margin: 10px;
        }
        .link-button-secondary {
            display: inline-block;
            background: white;
            color: #4f46e5;
            border: 2px solid #4f46e5;
            padding: 12px 30px;
            border-radius: 100px;
            text-decoration: none;
            font-weight: 600;
            margin: 10px;
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


# -------------------- PAGES --------------------
def show_chat_page():
    """Display the chat interface."""
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
            <div style="font-size: 11px; color: #cbd5e1; font-weight: 400; margin-top: 4px;">Built by Zayan Shahid</div>
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


def show_portfolio_page():
    """Display the portfolio page."""
    st.markdown("""
    <div class="portfolio-header">
        <div style="font-size: 48px; margin-bottom: 10px;">🧠</div>
        <h1 style="color: white; margin: 0; font-size: 36px; font-weight: 800;">Z.M.ai</h1>
        <p style="color: rgba(255,255,255,0.9); margin: 10px 0; font-size: 18px;">RAG-Based Academic Policy Assistant</p>
        <p style="color: rgba(255,255,255,0.8); margin: 0; font-size: 14px;">Built by Zayan Shahid</p>
    </div>
    """, unsafe_allow_html=True)

    # What is Z.M.ai
    st.markdown("""
    <div class="portfolio-section">
        <h2 style="color: #0f172a; font-weight: 700; font-size: 24px;">What is Z.M.ai?</h2>
        <p style="color: #475569; line-height: 1.8;">
            <strong>Navigate academic policies with confidence.</strong> Z.M.ai is an intelligent chatbot that delivers instant,
            accurate answers to university policy questions using advanced <strong>Retrieval-Augmented Generation (RAG)</strong> technology.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Key Features
    st.markdown("""
    <div class="portfolio-section">
        <h2 style="color: #0f172a; font-weight: 700; font-size: 24px;">Key Features</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px;">
    """, unsafe_allow_html=True)

    features = [
        ("🎯", "RAG-Powered Accuracy", "Retrieves real policy documents before generating responses"),
        ("⚡", "Lightning Fast", "Powered by Groq's Llama 3.1 models for instant responses"),
        ("📚", "Smart Knowledge Base", "Web scraping + PDF processing for comprehensive coverage"),
        ("💬", "Natural Conversations", "Chat naturally and get context-aware answers"),
        ("🎨", "Professional UI", "Clean, modern interface designed for students"),
        ("💾", "Local Caching", "Efficient local storage for fast loading"),
    ]

    for icon, title, desc in features:
        st.markdown(f"""
        <div class="feature-card">
            <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
            <h3 style="color: #0f172a; font-weight: 600; font-size: 16px; margin: 8px 0;">{title}</h3>
            <p style="color: #64748b; font-size: 13px; margin: 0;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # How It Works
    st.markdown("""
    <div class="portfolio-section">
        <h2 style="color: #0f172a; font-weight: 700; font-size: 24px;">How It Works</h2>
        <div style="display: flex; justify-content: space-between; gap: 15px; flex-wrap: wrap; margin-top: 20px;">
            <div style="flex: 1; min-width: 150px; text-align: center; padding: 15px; background: #f8fafc; border-radius: 12px;">
                <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #4f46e5, #8b5cf6); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; margin: 0 auto 10px;">1</div>
                <h4 style="margin: 8px 0; color: #0f172a;">Ask</h4>
                <p style="color: #64748b; font-size: 12px; margin: 0;">Type your question</p>
            </div>
            <div style="flex: 1; min-width: 150px; text-align: center; padding: 15px; background: #f8fafc; border-radius: 12px;">
                <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #4f46e5, #8b5cf6); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; margin: 0 auto 10px;">2</div>
                <h4 style="margin: 8px 0; color: #0f172a;">Retrieve</h4>
                <p style="color: #64748b; font-size: 12px; margin: 0;">Search policy documents</p>
            </div>
            <div style="flex: 1; min-width: 150px; text-align: center; padding: 15px; background: #f8fafc; border-radius: 12px;">
                <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #4f46e5, #8b5cf6); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; margin: 0 auto 10px;">3</div>
                <h4 style="margin: 8px 0; color: #0f172a;">Generate</h4>
                <p style="color: #64748b; font-size: 12px; margin: 0;">AI formulates answer</p>
            </div>
            <div style="flex: 1; min-width: 150px; text-align: center; padding: 15px; background: #f8fafc; border-radius: 12px;">
                <div style="width: 32px; height: 32px; background: linear-gradient(135deg, #4f46e5, #8b5cf6); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; margin: 0 auto 10px;">4</div>
                <h4 style="margin: 8px 0; color: #0f172a;">Respond</h4>
                <p style="color: #64748b; font-size: 12px; margin: 0;">Get accurate answer</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Tech Stack
    st.markdown("""
    <div class="portfolio-section">
        <h2 style="color: #0f172a; font-weight: 700; font-size: 24px;">Tech Stack</h2>
        <div style="text-align: center; margin-top: 20px;">
            <span class="tech-badge">🐍 Python</span>
            <span class="tech-badge">🌊 Streamlit</span>
            <span class="tech-badge">🚀 Groq API</span>
            <span class="tech-badge">📖 BeautifulSoup</span>
            <span class="tech-badge">📄 pdfplumber</span>
            <span class="tech-badge">🔍 Keyword Matching</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Project Stats
    st.markdown("""
    <div class="portfolio-section">
        <h2 style="color: #0f172a; font-weight: 700; font-size: 24px;">Project Highlights</h2>
        <div style="display: flex; justify-content: space-around; flex-wrap: wrap; gap: 20px; margin-top: 20px;">
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #4f46e5, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">380+</div>
                <div style="color: #64748b; font-size: 13px;">Lines of Code</div>
            </div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #4f46e5, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">&lt;2s</div>
                <div style="color: #64748b; font-size: 13px;">Response Time</div>
            </div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #4f46e5, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">100%</div>
                <div style="color: #64748b; font-size: 13px;">Free & Open</div>
            </div>
            <div style="text-align: center; flex: 1; min-width: 100px;">
                <div style="font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #4f46e5, #8b5cf6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">24/7</div>
                <div style="color: #64748b; font-size: 13px;">Available</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Links
    st.markdown("""
    <div class="portfolio-section">
        <h2 style="color: #0f172a; font-weight: 700; font-size: 24px;">Try It Now</h2>
        <div style="text-align: center; margin-top: 20px;">
            <a href="https://zaymavai.streamlit.app/" target="_blank" class="link-button">🚀 Live Demo</a>
            <a href="https://github.com/nubawan/Z.M.ai" target="_blank" class="link-button-secondary">💻 GitHub Repo</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Team
    st.markdown("""
    <div class="portfolio-section">
        <h2 style="color: #0f172a; font-weight: 700; font-size: 24px;">Built By</h2>
        <div style="text-align: center; margin-top: 20px;">
            <div style="display: inline-block; padding: 20px;">
                <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #4f46e5, #8b5cf6); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 0 auto 12px; color: white;">Z</div>
                <h3 style="color: #0f172a; font-weight: 600; font-size: 16px; margin: 8px 0;">Zayan Shahid</h3>
                <p style="color: #64748b; font-size: 13px; margin: 0;">Developer</p>
            </div>
        </div>
        <div style="text-align: center; margin-top: 20px; color: #64748b; font-size: 13px;">
            <p><strong>Course:</strong> Parallel & Distributed Computing</p>
            <p><strong>Instructor:</strong> Dr. Ali Akbar Siddique</p>
            <p><strong>Day/Time:</strong> Friday/Saturday, 8:30-9:50 AM</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# -------------------- MAIN APP --------------------
def main():
    """Main application with page navigation."""
    # Page config
    st.set_page_config(
        page_title="Z.M.ai | Academic Policy Assistant",
        page_icon="🧠",
        layout="centered"
    )

    # Inject CSS
    inject_custom_css()

    # Page navigation
    pg = st.navigation([
        st.Page(show_chat_page, title="💬 Chat", icon="💬"),
        st.Page(show_portfolio_page, title="📊 Portfolio", icon="📊"),
    ])
    pg.run()


if __name__ == "__main__":
    main()
