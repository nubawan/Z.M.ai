"""
Z.M.ai - UI Components

Professional, polished UI components for the Streamlit application.
"""

import logging
from typing import Optional, List, Callable

import streamlit as st

from config import get_ui_config
from .styles import (
    COLORS,
    format_user_message,
    format_assistant_message,
    format_error_message,
    get_typing_indicator_html,
)

logger = logging.getLogger(__name__)


def render_header(
    show_clear_button: bool = True,
    on_clear: Optional[Callable] = None,
    status_text: str = "Ready",
    status_color: str = "green",
) -> None:
    """
    Render the application header - professional design.

    Args:
        show_clear_button: Whether to show the clear chat button
        on_clear: Optional callback when clear is clicked
        status_text: Status text to display
        status_color: Color of the status indicator (green, red, amber)
    """
    ui_config = get_ui_config()

    # Header container with glass effect
    st.markdown(f"""
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 24px;
        background: {COLORS['bg_glass_strong']};
        backdrop-filter: blur(24px) saturate(180%);
        -webkit-backdrop-filter: blur(24px) saturate(180%);
        border-bottom: 1px solid {COLORS['border_subtle']};
        margin: -20px -20px 20px -20px;
    ">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, {COLORS['primary_start']}, {COLORS['primary_mid']});
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                box-shadow: 0 4px 12px {COLORS['accent_glow']};
            ">🧠</div>
            <div>
                <div style="
                    font-size: 22px;
                    font-weight: 700;
                    color: {COLORS['text_primary']};
                    letter-spacing: -0.03em;
                    line-height: 1.2;
                ">{ui_config.app_title}</div>
                <div style="
                    font-size: 13px;
                    color: {COLORS['text_tertiary']};
                    font-weight: 500;
                    margin-top: 2px;
                ">{ui_config.app_subtitle}</div>
            </div>
        </div>
        <div style="display: flex; align-items: center; gap: 12px;">
    </div>
    """, unsafe_allow_html=True)

    # Status indicator and clear button side by side
    col1, col2 = st.columns([1, 1])

    with col1:
        status_colors = {
            "green": COLORS["success"],
            "red": COLORS["error"],
            "amber": COLORS["warning"],
        }
        dot_color = status_colors.get(status_color, COLORS["success"])

        st.markdown(f"""
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 14px;
            background: {COLORS['bg_secondary']};
            border-radius: 9999px;
            font-size: 13px;
            border: 1px solid {COLORS['border_subtle']};
        ">
            <div style="
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: {dot_color};
                box-shadow: 0 0 10px {dot_color}60;
                animation: pulse 2s infinite;
            "></div>
            <span style="color: {COLORS['text_secondary']}; font-weight: 500;">{status_text}</span>
        </div>
        <style>
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
        </style>
        """, unsafe_allow_html=True)

    with col2:
        # Clear button
        if show_clear_button:
            if st.button("Clear Chat", key="header_clear", use_container_width=True):
                if on_clear:
                    on_clear()
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_welcome_message() -> None:
    """Render the welcome message shown to new users - professional design."""
    ui_config = get_ui_config()

    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 60px 40px;
        animation: fadeInUp 0.5s ease-out;
    ">
        <div style="
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 72px;
            height: 72px;
            background: linear-gradient(135deg, {COLORS['primary_start']}, {COLORS['primary_mid']});
            border-radius: 24px;
            font-size: 36px;
            margin-bottom: 24px;
            box-shadow: 0 8px 24px {COLORS['accent_glow']};
        ">🧠</div>
        <div style="
            font-size: 28px;
            font-weight: 700;
            color: {COLORS['text_primary']};
            margin-bottom: 12px;
            letter-spacing: -0.02em;
        ">
            Welcome to {ui_config.app_title}
        </div>
        <div style="
            color: {COLORS['text_secondary']};
            font-size: 15px;
            line-height: 1.7;
            max-width: 400px;
            margin: 0 auto;
        ">
            {ui_config.app_subtitle}
        </div>
    </div>
    <style>
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
    </style>
    """, unsafe_allow_html=True)

    # Display welcome message content
    st.markdown(f"""
    <div style="
        text-align: center;
        color: {COLORS['text_secondary']};
        font-size: 14px;
        line-height: 1.8;
        padding: 0 40px 40px;
        max-width: 500px;
        margin: 0 auto;
    ">
        {ui_config.welcome_message.replace('•', '<span style="color: ' + COLORS['primary_start'] + ';">•</span>')}
    </div>
    """, unsafe_allow_html=True)


def render_message(
    role: str,
    content: str,
    sources: Optional[List[str]] = None,
    show_avatar: bool = True,
) -> None:
    """
    Render a chat message.

    Args:
        role: "user" or "assistant"
        content: Message content (markdown supported)
        sources: Optional list of source citations
        show_avatar: Whether to show avatar
    """
    if role == "user":
        st.markdown(format_user_message(content), unsafe_allow_html=True)
    elif role == "assistant":
        # Use st.markdown for proper markdown rendering
        st.markdown(content, unsafe_allow_html=True)

        # Add sources if present
        if sources:
            source_tags = "".join([f'<span class="source-tag">{s}</span>' for s in sources])
            st.markdown(f"""
            <div class="sources-container" style="margin-top: 16px;">
                <div style="font-size: 11px; color: {COLORS['text_tertiary']}; font-weight: 500; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.05em;">
                    Sources
                </div>
                {source_tags}
            </div>
            """, unsafe_allow_html=True)
    elif role == "error":
        st.markdown(format_error_message(content), unsafe_allow_html=True)


def render_typing_indicator() -> None:
    """Render a typing indicator to show the bot is thinking."""
    st.markdown(get_typing_indicator_html(), unsafe_allow_html=True)


def render_input_area(
    placeholder: str = "Ask about academic policies...",
            disabled: bool = False,
) -> str:
    """
    Render the chat input area.

    Args:
        placeholder: Input placeholder text
        disabled: Whether input is disabled

    Returns:
        User input text
    """
    # Use Streamlit's chat input
    user_input = st.chat_input(
        placeholder=placeholder,
        disabled=disabled,
    )

    return user_input or ""


def render_sidebar() -> dict:
    """
    Render the sidebar with title and about info.

    Returns:
        Empty dictionary
    """
    with st.sidebar:
        st.markdown(f"""
        <div style="
            text-align: center;
            padding: 24px 0;
            margin-bottom: 20px;
            border-bottom: 1px solid {COLORS['border_subtle']};
        ">
            <div style="
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, {COLORS['primary_start']}, {COLORS['primary_mid']});
                border-radius: 14px;
                font-size: 24px;
                margin-bottom: 12px;
                box-shadow: 0 4px 12px {COLORS['accent_glow']};
            ">🧠</div>
            <div style="
                font-size: 18px;
                font-weight: 700;
                color: {COLORS['text_primary']};
                margin-bottom: 4px;
            ">{get_ui_config().app_title}</div>
            <div style="
                font-size: 12px;
                color: {COLORS['text_tertiary']};
            ">{get_ui_config().app_subtitle}</div>
        </div>
        """, unsafe_allow_html=True)

        # About section
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0;">
            <div style="font-size: 12px; color: {COLORS['text_tertiary']}; line-height: 1.8;">
                <strong style="color: {COLORS['text_primary']};">{get_ui_config().app_title}</strong><br>
                RAG-based Policy Assistant<br><br>
                Built with Streamlit + Groq
            </div>
        </div>
        """, unsafe_allow_html=True)

    return {}


def render_footer() -> None:
    """Render the footer with attribution - minimal design."""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 24px;
        color: {COLORS['text_tertiary']};
        font-size: 12px;
        border-top: 1px solid {COLORS['border_subtle']};
        margin-top: 40px;
    ">
        {get_ui_config().app_title} • Academic Policy Assistant
    </div>
    """, unsafe_allow_html=True)


def render_error_state(error_message: str) -> None:
    """
    Render an error state when something goes wrong - professional design.

    Args:
        error_message: Error message to display
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 80px 40px;
        background: {COLORS['bg_glass']};
        backdrop-filter: blur(24px) saturate(180%);
        -webkit-backdrop-filter: blur(24px) saturate(180%);
        border-radius: 24px;
        border: 1px solid {COLORS['border_subtle']};
        margin: 40px 0;
    ">
        <div style="
            font-size: 48px;
            margin-bottom: 20px;
            opacity: 0.8;
        ">⚠️</div>
        <div style="
            font-size: 18px;
            font-weight: 600;
            color: {COLORS['text_primary']};
            margin-bottom: 8px;
        ">Initialization Failed</div>
        <div style="
            color: {COLORS['text_secondary']};
            font-size: 14px;
            line-height: 1.6;
            max-width: 400px;
            margin: 0 auto;
        ">
            {error_message}
        </div>
        <div style="
            margin-top: 24px;
            font-size: 13px;
            color: {COLORS['text_tertiary']};
        ">Please try refreshing the page</div>
    </div>
    """, unsafe_allow_html=True)


def render_loading_state(message: str = "Loading knowledge base...") -> None:
    """
    Render a loading state - professional design.

    Args:
        message: Loading message to display
    """
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 80px 40px;
    ">
        <div class="typing-indicator" style="justify-content: center; margin-bottom: 24px; gap: 8px;">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
        <div style="
            color: {COLORS['text_secondary']};
            font-size: 15px;
            font-weight: 500;
        ">{message}</div>
    </div>
    """, unsafe_allow_html=True)
