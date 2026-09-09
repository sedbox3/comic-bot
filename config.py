"""Configuration management for the comic translation pipeline."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class Config:
    """Pipeline configuration loaded from environment / .env file."""

    # LLM Provider
    llm_api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    llm_base_url: str = field(default_factory=lambda: os.getenv("LLM_BASE_URL", "https://api.orcarouter.ai/v1"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "z-ai/glm-5.3-flash-free"))

    # OCR
    ocr_backend: str = field(default_factory=lambda: os.getenv("OCR_BACKEND", "rapidocr"))

    # Inpainting
    inpaint_method: str = field(default_factory=lambda: os.getenv("INPAINT_METHOD", "ns"))
    inpaint_radius: int = field(default_factory=lambda: int(os.getenv("INPAINT_RADIUS", "7")))

    # Typesetting
    font_path: str = field(default_factory=lambda: os.getenv("FONT_PATH", ""))
    font_size: int = field(default_factory=lambda: int(os.getenv("FONT_SIZE", "16")))
    text_color: str = field(default_factory=lambda: os.getenv("TEXT_COLOR", "0,0,0"))

    # System prompt
    system_prompt: str = field(default_factory=lambda: os.getenv("SYSTEM_PROMPT", ""))

    # Telegram Bot (for bot integration)
    telegram_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))

    # Processing
    max_file_size_mb: int = field(default_factory=lambda: int(os.getenv("MAX_FILE_SIZE_MB", "50")))
    temp_dir: str = field(default_factory=lambda: os.getenv("TEMP_DIR", ""))

    def validate(self) -> list:
        """Return list of validation errors."""
        errors = []
        if not self.llm_api_key:
            errors.append("LLM_API_KEY is not set")
        return errors


def load_config() -> Config:
    """Load configuration from environment variables and .env file."""
    return Config()


# Example .env content for reference
ENV_EXAMPLE = """# ===== LLM Provider Configuration =====
# Get free API key from: https://orcarouter.ai
LLM_API_KEY=sk-orca-your-key-here

# OrcaRouter (free models available)
LLM_BASE_URL=https://api.orcarouter.ai/v1
LLM_MODEL=z-ai/glm-5.3-flash-free

# Alternative: Google Gemini (free tier)
# LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
# LLM_MODEL=gemini-2.0-flash

# Alternative: Groq (free tier)
# LLM_BASE_URL=https://api.groq.com/openai/v1
# LLM_MODEL=llama-3.1-8b-instant

# ===== OCR Configuration =====
OCR_BACKEND=tesseract
# Options: tesseract, easyocr

# ===== Inpainting Configuration =====
INPAINT_METHOD=ns
# Options: ns (Navier-Stokes), telea, lama
INPAINT_RADIUS=7

# ===== Typesetting Configuration =====
# Path to Arabic TTF font (leave empty for default)
FONT_PATH=
FONT_SIZE=16
TEXT_COLOR=0,0,0

# ===== Telegram Bot (optional) =====
# TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# ===== Processing Limits =====
MAX_FILE_SIZE_MB=50
"""
