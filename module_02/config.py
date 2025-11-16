"""
Configuration for AI News Bulletin Generator (Module 02)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================================================
# PATHS CONFIGURATION
# ============================================================================

# Base paths
MODULE_DIR = Path(__file__).parent
PROJECT_ROOT = MODULE_DIR.parent
OUTPUT_DIR = MODULE_DIR / "output"  # Output inside module_02

# Database path (from module_01)
NEWS_DB_PATH = PROJECT_ROOT / "module_01" / "output" / "news.db"

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================================
# GEMINI API CONFIGURATION
# ============================================================================

# API Key from environment variable or AI Studio
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found! Please set it in .env file or environment.\n"
        "Get your API key from: https://aistudio.google.com/apikey"
    )

# Model selection
GEMINI_MODEL = "gemini-2.5-flash"  # Best price-performance with thinking
GEMINI_FALLBACK_MODEL = "gemini-2.5-flash-lite"  # Fallback model (faster, more stable)

# Generation configuration
GENERATION_CONFIG = {
    "temperature": 0.7,  # Balance between creativity and consistency
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# Thinking configuration
THINKING_CONFIG = {
    "thinking_budget": -1,  # Dynamic thinking (model decides)
    "include_thoughts": True,  # Get thought summaries for debugging
}

# ============================================================================
# BULLETIN GENERATION SETTINGS
# ============================================================================

# Content settings
MIN_STORIES = 3  # Minimum number of stories in bulletin
MAX_STORIES = 7  # Maximum number of stories in bulletin
MIN_ARTICLES_REQUIRED = 2  # Minimum articles needed to generate bulletin

# Story priority thresholds
HIGH_PRIORITY_THRESHOLD = 8  # Score >= 8 = high priority
MEDIUM_PRIORITY_THRESHOLD = 5  # Score >= 5 = medium priority

# Text formatting for TTS
TTS_SETTINGS = {
    "add_intro": True,  # Add bulletin introduction
    "add_outro": True,  # Add bulletin closing
    "add_transitions": True,  # Add transitions between stories
    "max_sentence_length": 200,  # Maximum characters per sentence for TTS
}

# ============================================================================
# BULLETIN STYLE CONFIGURATION
# ============================================================================

BULLETIN_INTRO_TEMPLATE = "Bản tin công nghệ ngày {date_vietnamese}"
BULLETIN_GREETING = "Chào mừng quý vị đến với bản tin công nghệ hôm nay."
BULLETIN_OUTRO = "Đó là những tin công nghệ nổi bật trong ngày hôm qua. Cảm ơn quý vị đã theo dõi."

# Story transitions
STORY_TRANSITIONS = [
    "Tin nổi bật đầu tiên:",
    "Tiếp theo,",
    "Trong khi đó,",
    "Một tin khác,",
    "Ngoài ra,",
    "Cuối cùng,",
]

# ============================================================================
# DATE CONFIGURATION
# ============================================================================

# Date format for Vietnamese display
VIETNAMESE_DATE_FORMAT = "%d tháng %m năm %Y"

# Weekday names in Vietnamese
VIETNAMESE_WEEKDAYS = {
    0: "Thứ Hai",
    1: "Thứ Ba",
    2: "Thứ Tư",
    3: "Thứ Năm",
    4: "Thứ Sáu",
    5: "Thứ Sáu",
    6: "Chủ Nhật",
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# ERROR HANDLING
# ============================================================================

# Retry settings for API calls
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
RETRY_BACKOFF = 2  # exponential backoff multiplier

# Fallback settings
FALLBACK_TO_TWO_DAYS = True  # If not enough articles from yesterday
FALLBACK_MIN_ARTICLES = 5  # Minimum articles when falling back
