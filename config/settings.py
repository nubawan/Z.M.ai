"""
Z.M.ai - Configuration Management

Dynamic configuration system that loads from:
1. Streamlit secrets (.streamlit/secrets.toml) - Priority 1
2. Environment variables (.env) - Priority 2
3. Default values - Priority 3
"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List
from functools import lru_cache
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file (if exists)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)


@dataclass
class GroqConfig:
    """Groq API configuration."""
    api_key: str = ""
    model_name: str = "llama-3.1-8b-instant"
    temperature: float = 0.3
    max_tokens: int = 2048
    timeout: int = 30

    def __post_init__(self):
        """Validate and load API key from various sources."""
        # Priority 1: Streamlit secrets
        if "GROQ_API_KEY" in st.secrets:
            self.api_key = st.secrets["GROQ_API_KEY"]
        # Priority 2: Environment variable
        elif env_key := os.getenv("GROQ_API_KEY"):
            self.api_key = env_key
        # Priority 3: Use whatever was set (or empty)

        # Load model from secrets or env if available
        if "MODEL_NAME" in st.secrets:
            self.model_name = st.secrets["MODEL_NAME"]
        elif model := os.getenv("MODEL_NAME"):
            self.model_name = model

        if not self.api_key:
            logger.warning("GROQ_API_KEY not configured")


@dataclass
class RAGConfig:
    """RAG (Retrieval-Augmented Generation) configuration."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 8
    similarity_threshold: float = 0.25
    embedding_model: str = "all-MiniLM-L6-v2"

    def __post_init__(self):
        """Load RAG settings from environment and Streamlit secrets."""
        if "CHUNK_SIZE" in st.secrets:
            self.chunk_size = int(st.secrets["CHUNK_SIZE"])
        elif chunk_size := os.getenv("CHUNK_SIZE"):
            self.chunk_size = int(chunk_size)

        if "CHUNK_OVERLAP" in st.secrets:
            self.chunk_overlap = int(st.secrets["CHUNK_OVERLAP"])
        elif chunk_overlap := os.getenv("CHUNK_OVERLAP"):
            self.chunk_overlap = int(chunk_overlap)

        if "TOP_K_RESULTS" in st.secrets:
            self.top_k_results = int(st.secrets["TOP_K_RESULTS"])
        elif top_k := os.getenv("TOP_K_RESULTS"):
            self.top_k_results = int(top_k)

        if "SIMILARITY_THRESHOLD" in st.secrets:
            self.similarity_threshold = float(st.secrets["SIMILARITY_THRESHOLD"])
        elif threshold := os.getenv("SIMILARITY_THRESHOLD"):
            self.similarity_threshold = float(threshold)




@dataclass
class DataSourceConfig:
    """Data source configuration."""

    default_pdf_path: str = "reference/Academic-Policy-Manual-for-Students2.pdf"
    scrape_url: str = "https://iqra.edu.pk/iu-policies/"
    scrape_enabled: bool = True
    cache_dir: str = "data/cache"
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parents[1], init=False)

    def __post_init__(self):
        """Load data source settings from environment and Streamlit secrets."""

        # Priority 1: Streamlit secrets, Priority 2: Environment variables
        if "DEFAULT_PDF_PATH" in st.secrets:
            self.default_pdf_path = st.secrets["DEFAULT_PDF_PATH"]
        elif pdf_path := os.getenv("DEFAULT_PDF_PATH"):
            self.default_pdf_path = pdf_path

        if "SCRAPE_URL" in st.secrets:
            self.scrape_url = st.secrets["SCRAPE_URL"]
        elif scrape_url := os.getenv("SCRAPE_URL"):
            self.scrape_url = scrape_url

        if "SCRAPE_ENABLED" in st.secrets:
            self.scrape_enabled = str(st.secrets["SCRAPE_ENABLED"]).lower() in ("true", "1", "yes")
        elif scrape_enabled := os.getenv("SCRAPE_ENABLED"):
            self.scrape_enabled = scrape_enabled.lower() in ("true", "1", "yes")

        if "CACHE_DIR" in st.secrets:
            self.cache_dir = st.secrets["CACHE_DIR"]
        elif cache_dir := os.getenv("CACHE_DIR"):
            self.cache_dir = cache_dir

        # Convert to absolute paths (critical for Streamlit)
        self.default_pdf_path = str(self.project_root / self.default_pdf_path)
        self.cache_dir = str(self.project_root / self.cache_dir)


@dataclass
class UIConfig:
    """UI configuration."""
    app_title: str = "Z.M.ai"
    app_subtitle: str = "RAG-based Academic Policy Assistant"
    max_history: int = 50
    theme_color: str = "#8b5cf6"
    show_sources: bool = True
    welcome_message: str = (
        "👋 Welcome to **Z.M.ai**! I'm your academic policy assistant.\n\n"
        "I can help you find information about:\n"
        "• Academic policies and procedures\n"
        "• Grading and attendance requirements\n"
        "• Course registration and drop/add policies\n"
        "• Exam schedules and requirements\n\n"
        "Feel free to ask me anything about university policies!"
    )

    def __post_init__(self):
        """Load UI settings from environment and Streamlit secrets."""
        if "APP_TITLE" in st.secrets:
            self.app_title = st.secrets["APP_TITLE"]
        elif title := os.getenv("APP_TITLE"):
            self.app_title = title

        if "MAX_HISTORY" in st.secrets:
            self.max_history = int(st.secrets["MAX_HISTORY"])
        elif max_hist := os.getenv("MAX_HISTORY"):
            self.max_history = int(max_hist)

        if "THEME_COLOR" in st.secrets:
            self.theme_color = st.secrets["THEME_COLOR"]
        elif color := os.getenv("THEME_COLOR"):
            self.theme_color = color


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    def __post_init__(self):
        """Load logging settings from environment."""
        if level := os.getenv("LOG_LEVEL"):
            self.level = level.upper()


@dataclass
class Config:
    """Main configuration class holding all sub-configurations."""
    groq: GroqConfig = field(default_factory=GroqConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    data_source: DataSourceConfig = field(default_factory=DataSourceConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent

    @property
    def data_dir(self) -> Path:
        """Get the data directory."""
        return self.project_root / "data"

    @property
    def pdfs_dir(self) -> Path:
        """Get the PDFs directory."""
        return self.data_dir / "pdfs"

    def validate(self) -> bool:
        """
        Validate configuration.
        Returns True if valid, raises ValueError otherwise.
        """
        errors = []

        # Validate Groq API key
        if not self.groq.api_key:
            errors.append("GROQ_API_KEY is required")

        # Validate RAG settings
        if self.rag.chunk_size <= 0:
            errors.append("CHUNK_SIZE must be positive")
        if self.rag.chunk_overlap < 0:
            errors.append("CHUNK_OVERLAP must be non-negative")
        if self.rag.chunk_overlap >= self.rag.chunk_size:
            errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")
        if not (0 <= self.rag.similarity_threshold <= 1):
            errors.append("SIMILARITY_THRESHOLD must be between 0 and 1")

        if errors:
            raise ValueError("Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

        return True

    def setup_logging(self):
        """Setup logging based on configuration."""
        log_level = getattr(logging, self.logging.level, logging.INFO)
        logging.basicConfig(
            level=log_level,
            format=self.logging.format,
            force=True
        )
        logger.setLevel(log_level)


@lru_cache
def get_config() -> Config:
    """
    Get the singleton configuration instance.
    This is cached to avoid reloading configuration on every call.
    """
    config = Config()
    config.setup_logging()
    return config


def get_config_with_validation() -> Config:
    """
    Get configuration with validation.
    Raises ValueError if configuration is invalid.
    """
    config = get_config()
    config.validate()
    return config


# Convenience functions for accessing config in Streamlit
def get_groq_config() -> GroqConfig:
    """Get Groq configuration."""
    return get_config().groq


def get_rag_config() -> RAGConfig:
    """Get RAG configuration."""
    return get_config().rag


def get_data_source_config() -> DataSourceConfig:
    """Get data source configuration."""
    return get_config().data_source


def get_ui_config() -> UIConfig:
    """Get UI configuration."""
    return get_config().ui
