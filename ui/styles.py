"""
Z.M.ai - UI Styles

Professional, polished CSS styling for the Streamlit application.
"""

from config import get_ui_config

# Get configuration for dynamic colors
ui_config = get_ui_config()

# Professional color palette - more refined
COLORS = {
    "primary_start": "#4f46e5",    # Indigo 600
    "primary_mid": ui_config.theme_color,  # Configurable (default: #8b5cf6)
    "primary_end": "#7c3aed",      # Violet 600
    "accent_glow": "rgba(79, 70, 229, 0.15)",
    "bg_primary": "#ffffff",
    "bg_secondary": "#f8fafc",
    "bg_glass": "rgba(255, 255, 255, 0.9)",
    "bg_glass_strong": "rgba(255, 255, 255, 0.95)",
    "text_primary": "#0f172a",
    "text_secondary": "#475569",
    "text_tertiary": "#94a3b8",
    "border_subtle": "rgba(148, 163, 184, 0.2)",
    "border_medium": "rgba(148, 163, 184, 0.3)",
    "success": "#22c55e",
    "error": "#ef4444",
    "warning": "#f59e0b",
}


def get_gradient_css() -> str:
    """Get the animated gradient background CSS - more subtle."""
    return f"""
    <style>
        /* Main app background - subtle animated gradient */
        .stApp {{
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 50%, #f1f5f9 100%);
            background-attachment: fixed;
        }}

        /* Subtle animated accent gradient overlay */
        .stApp::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(ellipse at 20% 20%, rgba(79, 70, 229, 0.05) 0%, transparent 50%),
                        radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
            animation: subtleShift 20s ease-in-out infinite;
        }}

        @keyframes subtleShift {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}

        /* Hide default Streamlit background */
        .stApp >> div[data-testid="stAppViewContainer"] > div > div {{
            background: transparent;
        }}

        /* Main container with proper z-index */
        .stApp >> [data-testid="stAppViewContainer"] {{
            position: relative;
            z-index: 1;
        }}
    </style>
    """


def get_glassmorphism_css() -> str:
    """Get glassmorphism effect CSS - more refined."""
    return f"""
    <style>
        /* Glassmorphism container - cleaner look */
        .glass-container {{
            background: {COLORS["bg_glass_strong"]};
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            border-radius: 20px;
            border: 1px solid {COLORS["border_subtle"]};
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 8px 30px rgba(0, 0, 0, 0.08);
        }}

        /* Glassmorphic header */
        .glass-header {{
            background: {COLORS["bg_glass_strong"]};
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            border-bottom: 1px solid {COLORS["border_subtle"]};
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
        }}

        /* Glassmorphic input area */
        .glass-input {{
            background: {COLORS["bg_glass_strong"]};
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            border-top: 1px solid {COLORS["border_subtle"]};
        }}
    </style>
    """


def get_message_css() -> str:
    """Get message bubble styling CSS - more polished."""
    return f"""
    <style>
        /* Message containers - refined animations */
        .message-container {{
            display: flex;
            gap: 12px;
            padding: 4px 0;
            animation: messageFadeIn 0.3s ease-out;
        }}

        @keyframes messageFadeIn {{
            from {{
                opacity: 0;
                transform: translateY(8px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        /* User message - more refined gradient */
        .message-user {{
            background: linear-gradient(135deg, {COLORS["primary_start"]} 0%, {COLORS["primary_mid"]} 100%);
            color: white;
            padding: 14px 20px;
            border-radius: 20px 20px 4px 20px;
            box-shadow: 0 2px 8px {COLORS["accent_glow"]};
            max-width: 75%;
            margin-left: auto;
            font-size: 15px;
            line-height: 1.5;
            font-weight: 400;
        }}

        /* Assistant message - cleaner white design */
        .message-assistant {{
            background: white;
            color: {COLORS["text_primary"]};
            padding: 14px 20px;
            border-radius: 20px 20px 20px 4px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06), 0 8px 20px rgba(0, 0, 0, 0.06);
            border: 1px solid {COLORS["border_subtle"]};
            max-width: 85%;
            font-size: 15px;
            line-height: 1.6;
        }}

        /* Assistant message markdown styling */
        .message-assistant h1, .message-assistant h2, .message-assistant h3 {{
            margin-top: 0;
            margin-bottom: 8px;
            font-weight: 600;
            color: {COLORS["text_primary"]};
        }}

        .message-assistant h1 {{ font-size: 1.4em; }}
        .message-assistant h2 {{ font-size: 1.25em; }}
        .message-assistant h3 {{ font-size: 1.1em; }}

        .message-assistant ul, .message-assistant ol {{
            margin: 8px 0;
            padding-left: 20px;
        }}

        .message-assistant li {{
            margin: 4px 0;
            line-height: 1.6;
        }}

        .message-assistant p {{
            margin: 8px 0;
        }}

        .message-assistant code {{
            background: {COLORS["bg_secondary"]};
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
        }}

        .message-assistant strong {{
            font-weight: 600;
            color: {COLORS["text_primary"]};
        }}

        /* Error message - more professional */
        .message-error {{
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(239, 68, 68, 0.04) 100%);
            color: #dc2626;
            padding: 14px 20px;
            border-radius: 12px;
            border-left: 3px solid {COLORS["error"]};
            font-size: 14px;
        }}
    </style>
    """


def get_source_tag_css() -> str:
    """Get source tag styling CSS - cleaner look."""
    return f"""
    <style>
        /* Source tags - more refined */
        .source-tag {{
            background: {COLORS["bg_secondary"]};
            color: {COLORS["text_secondary"]};
            padding: 5px 11px;
            border-radius: 8px;
            font-size: 11px;
            font-weight: 500;
            display: inline-block;
            margin: 4px 6px 4px 0;
            border: 1px solid {COLORS["border_subtle"]};
            transition: all 0.2s ease;
            font-family: 'SF Mono', 'Monaco', 'Cascadia Code', monospace;
            letter-spacing: -0.01em;
        }}

        .source-tag:hover {{
            background: {COLORS["primary_start"]};
            color: white;
            border-color: {COLORS["primary_start"]};
            transform: translateY(-1px);
        }}

        .sources-container {{
            margin-top: 14px;
            padding-top: 14px;
            border-top: 1px solid {COLORS["border_subtle"]};
        }}

        .sources-container > div:first-child {{
            font-size: 11px;
            color: {COLORS["text_tertiary"]};
            font-weight: 500;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
    </style>
    """


def get_typing_indicator_css() -> str:
    """Get typing indicator animation CSS - refined."""
    return f"""
    <style>
        /* Typing indicator */
        .typing-indicator {{
            display: flex;
            gap: 5px;
            padding: 12px 0;
            align-items: center;
        }}

        .typing-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: linear-gradient(135deg, {COLORS["primary_start"]}, {COLORS["primary_mid"]});
            animation: typingPulse 1.3s infinite ease-in-out;
        }}

        .typing-dot:nth-child(2) {{
            animation-delay: 0.15s;
        }}

        .typing-dot:nth-child(3) {{
            animation-delay: 0.3s;
        }}

        @keyframes typingPulse {{
            0%, 100% {{
                opacity: 0.3;
                transform: scale(0.85);
            }}
            50% {{
                opacity: 1;
                transform: scale(1);
            }}
        }}
    </style>
    """


def get_custom_scrollbar_css() -> str:
    """Get custom scrollbar CSS - cleaner."""
    return f"""
    <style>
        /* Custom scrollbar - more refined */
        [data-testid="stVerticalBlock"] > div > div > div > div {{
            scrollbar-width: thin;
            scrollbar-color: {COLORS["border_medium"]} transparent;
        }}

        [data-testid="stVerticalBlock"] > div > div > div > div::-webkit-scrollbar {{
            width: 6px;
        }}

        [data-testid="stVerticalBlock"] > div > div > div > div::-webkit-scrollbar-track {{
            background: transparent;
        }}

        [data-testid="stVerticalBlock"] > div > div > div > div::-webkit-scrollbar-thumb {{
            background: {COLORS["border_medium"]};
            border-radius: 10px;
            border: 2px solid transparent;
            background-clip: content-box;
        }}

        [data-testid="stVerticalBlock"] > div > div > div > div::-webkit-scrollbar-thumb:hover {{
            background: {COLORS["text_tertiary"]};
            background-clip: content-box;
        }}
    </style>
    """


def get_chat_input_css() -> str:
    """Get chat input styling CSS - professional."""
    return f"""
    <style>
        /* Chat input container */
        .stChatInputContainer {{
            border-top: 1px solid {COLORS["border_subtle"]} !important;
            background: {COLORS["bg_glass_strong"]} !important;
            backdrop-filter: blur(24px) saturate(180%);
            -webkit-backdrop-filter: blur(24px) saturate(180%);
            padding: 16px 20px !important;
        }}

        /* Chat input field */
        .stChatInputContainer textarea {{
            background: {COLORS["bg_secondary"]} !important;
            border: 1px solid {COLORS["border_subtle"]} !important;
            border-radius: 14px !important;
            padding: 14px 18px !important;
            font-size: 15px !important;
            color: {COLORS["text_primary"]} !important;
            transition: all 0.2s ease !important;
            resize: none !important;
        }}

        .stChatInputContainer textarea:focus {{
            border-color: {COLORS["primary_start"]} !important;
            box-shadow: 0 0 0 3px {COLORS["accent_glow"]} !important;
            outline: none !important;
        }}

        .stChatInputContainer textarea::placeholder {{
            color: {COLORS["text_tertiary"]} !important;
        }}

        /* Send button */
        .stChatInputContainer button {{
            background: linear-gradient(135deg, {COLORS["primary_start"]}, {COLORS["primary_mid"]}) !important;
            border: none !important;
            border-radius: 12px !important;
            color: white !important;
            transition: all 0.2s ease !important;
        }}

        .stChatInputContainer button:hover {{
            transform: scale(1.02);
            box-shadow: 0 4px 12px {COLORS["accent_glow"]} !important;
        }}
    </style>
    """


def get_button_css() -> str:
    """Get button styling CSS - professional."""
    return f"""
    <style>
        /* General button styling */
        .stButton > button {{
            background: white;
            color: {COLORS["text_primary"]};
            border: 1px solid {COLORS["border_medium"]};
            border-radius: 10px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }}

        .stButton > button:hover {{
            background: {COLORS["bg_secondary"]};
            border-color: {COLORS["text_tertiary"]};
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.08);
        }}
    </style>
    """


def get_all_css() -> str:
    """
    Combine all CSS into a single string for injection.

    Returns:
        Complete CSS string for use in st.markdown()
    """
    return "".join([
        get_gradient_css(),
        get_glassmorphism_css(),
        get_message_css(),
        get_source_tag_css(),
        get_typing_indicator_css(),
        get_custom_scrollbar_css(),
        get_chat_input_css(),
        get_button_css(),
    ])


def inject_custom_css():
    """
    Inject all custom CSS into the Streamlit app.
    Call this once at the beginning of your app.
    """
    import streamlit as st
    st.markdown(get_all_css(), unsafe_allow_html=True)


def format_user_message(content: str) -> str:
    """Format a user message for display."""
    return f"""
    <div class="message-container">
        <div class="message-user">
            {content}
        </div>
    </div>
    """


def format_assistant_message(content: str, sources: list = None) -> str:
    """
    Format an assistant message for display.

    Args:
        content: Message content (can include markdown)
        sources: Optional list of source strings

    Returns:
        HTML formatted message
    """
    # Convert markdown to HTML (basic conversion)
    # Note: For full markdown support, use st.markdown() separately
    formatted_content = content.replace("\n", "<br>")

    source_html = ""
    if sources:
        source_tags = "".join([f'<span class="source-tag">{source}</span>' for source in sources])
        source_html = f'<div class="sources-container"><div>Sources</div>{source_tags}</div>'

    return f"""
    <div class="message-container">
        <div class="message-assistant">
            {formatted_content}
            {source_html}
        </div>
    </div>
    """


def format_error_message(content: str) -> str:
    """Format an error message for display."""
    return f"""
    <div class="message-container">
        <div class="message-error">
            {content}
        </div>
    </div>
    """


def get_typing_indicator_html() -> str:
    """Get HTML for a typing indicator."""
    return """
    <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    </div>
    """
