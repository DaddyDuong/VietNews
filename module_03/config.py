"""
Configuration for TTS Automation Module (Module 03)
"""
import os
from pathlib import Path

# ============================================================================
# PATHS CONFIGURATION
# ============================================================================

# Base paths
MODULE_DIR = Path(__file__).parent
PROJECT_ROOT = MODULE_DIR.parent

# Input from module_02
MODULE_02_OUTPUT = PROJECT_ROOT / "module_02" / "output"

# Output directories
OUTPUT_DIR = MODULE_DIR / "output"  # Generated audio files
LOGS_DIR = MODULE_DIR / "logs"  # Log files

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# GOOGLE COLAB CONFIGURATION
# ============================================================================

# Colab notebook URL (to be set by user)
COLAB_NOTEBOOK_URL = os.getenv(
    "COLAB_NOTEBOOK_URL",
    "https://colab.research.google.com/drive/1u2rOjNuBmmmaO6EtkmapR0itwHL31eal"
)

# Timeouts (in seconds)
COLAB_PAGE_LOAD_TIMEOUT = 60
COLAB_RUNTIME_CONNECT_TIMEOUT = 300  # 5 minutes for GPU allocation
CELL_EXECUTION_TIMEOUT = 300  # 5 minutes per cell
GENERATION_TIMEOUT = 600  # 10 minutes for TTS generation
DOWNLOAD_TIMEOUT = 120  # 2 minutes for download

# ============================================================================
# BROWSER CONFIGURATION
# ============================================================================

BROWSER_TYPE = "chrome"  # "chrome" or "chromium"
HEADLESS = True  # Set to True for headless mode (no GUI)
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# Download directory
DOWNLOAD_DIR = str(OUTPUT_DIR.absolute())

# ============================================================================
# AUTHENTICATION CONFIGURATION
# ============================================================================

AUTH_METHOD = "cookies"  # "manual" or "cookies"
COOKIES_FILE = MODULE_DIR / "colab_cookies.json"

# ============================================================================
# NOTEBOOK CELL CONFIGURATION
# ============================================================================

# Cells to execute in order (by index, 0-based)
# Based on ZipVoice-Vietnamese-2500h.ipynb structure
CELLS_EXECUTION_ORDER = [
    2,   # Check GPU
    4,   # Setup: Clone repos & download reference audio
    6,   # Install dependencies
    8,   # Load model components
    10,  # Import preprocessing utilities
    12,  # Define inference function
    14,  # Generate speech (THIS WILL BE MODIFIED WITH BULLETIN)
    16,  # Play audio
    17,  # Download audio (will be added)
]

# Cell that contains TEXT_TO_SYNTHESIZE variable
TEXT_INPUT_CELL_INDEX = 14  # Cell index where we modify the text

# Identifier for finding the text variable in cell
TEXT_VARIABLE_NAME = "TEXT_TO_SYNTHESIZE"

# Output file path in Colab
COLAB_OUTPUT_PATH = "/content/output_vietnamese.wav"

# ============================================================================
# TTS GENERATION PARAMETERS
# ============================================================================

# Generation parameters
NUM_STEP = 8
SPEED = 1.0
REMOVE_LONG_SIL = False
MAX_DURATION = 100

# Reference audio (already in Colab notebook)
REFERENCE_AUDIO = "/content/reference_audio_3s.wav"
REFERENCE_TEXT = "Chào mừng quý vị và các bạn đã quay trở lại với kênh của chúng tôi."

# ============================================================================
# ERROR HANDLING CONFIGURATION
# ============================================================================

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds between retries

# Cell execution monitoring
CHECK_INTERVAL = 2  # Check cell status every 2 seconds

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_FILE = LOGS_DIR / "tts_automation.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# ============================================================================
# OUTPUT NAMING CONFIGURATION
# ============================================================================

# Output filename format: {date}.wav
OUTPUT_FILENAME_FORMAT = "{date}.wav"
