# Module 03 - TTS Automation for Vietnamese News Bulletins

## Overview

Module 03 automates the text-to-speech (TTS) generation process for Vietnamese news bulletins using Google Colab. It reads bulletin text files from Module 02, automates interaction with a Google Colab notebook containing a Vietnamese TTS model, and downloads the generated audio files.

## Features

- **Automated Colab Workflow**: Fully automated interaction with Google Colab notebooks using Selenium
- **Flexible Authentication**: Support for both manual login and cookie-based authentication
- **Bulletin Processing**: Reads and validates bulletin text from Module 02 output
- **Runtime Management**: Automatic connection and management of Colab runtime instances
- **Cell Execution**: Executes notebook cells sequentially with proper error handling
- **Audio Download**: Automatically downloads generated audio files to local output directory
- **Robust Error Handling**: Retry mechanisms and comprehensive logging

## Directory Structure

```
module_03/
├── main.py                     # Main orchestration script
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── colab_cookies.json         # Google authentication cookies (user-provided)
├── ZipVoice-Vietnamese-2500h.ipynb  # Reference TTS notebook
│
├── colab_automation/          # Colab automation components
│   ├── browser_driver.py      # Selenium WebDriver management
│   ├── auth_handler.py        # Google authentication handling
│   ├── colab_interface.py     # Colab UI interaction
│   └── cell_executor.py       # Notebook cell execution
│
├── input_handler/             # Input processing
│   └── bulletin_reader.py     # Read bulletins from module_02
│
├── output_handler/            # Output management
│   ├── audio_downloader.py    # Download generated audio files
│   └── file_manager.py        # Manage output files
│
├── utils/                     # Utility modules
│   ├── logger.py              # Logging configuration
│   ├── date_utils.py          # Date handling utilities
│   └── retry_handler.py       # Retry logic for operations
│
├── logs/                      # Log files
└── output/                    # Generated audio files
```

## Prerequisites

1. **Python 3.8+**
2. **Google Account** with access to Google Colab
3. **Chrome/Chromium Browser** installed
4. **Module 02** must be set up and have generated bulletin files
5. **Google Colab Notebook** with Vietnamese TTS model (ZipVoice or similar)

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Configure Google Colab URL in `config.py`:
```python
COLAB_NOTEBOOK_URL = "your_colab_notebook_url_here"
```

3. Set up authentication:

   **Option A - Cookie-based (Recommended):**
   - Login to Google Colab manually in your browser
   - Export cookies to `colab_cookies.json`
   - Set `AUTH_METHOD = "cookies"` in config

   **Option B - Manual login:**
   - Set `AUTH_METHOD = "manual"` in config
   - Browser will open for manual login during execution

## Configuration

Key settings in `config.py`:

```python
# Google Colab
COLAB_NOTEBOOK_URL = "your_colab_url"
COLAB_RUNTIME_CONNECT_TIMEOUT = 300  # 5 minutes
GENERATION_TIMEOUT = 600  # 10 minutes

# Browser
HEADLESS = True  # Set False to see browser window
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# Authentication
AUTH_METHOD = "cookies"  # "cookies" or "manual"
COOKIES_FILE = MODULE_DIR / "colab_cookies.json"

# Cell Indices (customize for your notebook)
TEXT_INPUT_CELL_INDEX = 0  # Cell where text is inserted
GENERATION_START_CELL = 0  # First cell to execute
GENERATION_END_CELL = 10   # Last cell to execute

# TTS Parameters
TTS_NUM_STEP = 16
TTS_SPEED = 0.85
TTS_REMOVE_LONG_SIL = False
TTS_MAX_DURATION = 100
```

## Usage

### Basic Usage

Process yesterday's bulletin:
```bash
python main.py
```

Process latest available bulletin:
```bash
python main.py --date latest
```

Process specific date:
```bash
python main.py --date 2025-11-15
```

### Command Line Arguments

```
--date DATE          Date of bulletin to process
                     Options: yesterday, today, latest, or YYYY-MM-DD
                     Default: yesterday

--colab-url URL      Google Colab notebook URL
                     Default: from config.py

--headless           Run browser in headless mode (no GUI)
                     Default: False (shows browser window)

--auth-method METHOD Authentication method
                     Options: manual, cookies
                     Default: cookies

--log-level LEVEL    Logging level
                     Options: DEBUG, INFO, WARNING, ERROR
                     Default: INFO

--output-dir DIR     Output directory for audio files
                     Default: ./output
```

### Examples

Process today's bulletin with visible browser:
```bash
python main.py --date today
```

Process specific date with manual authentication:
```bash
python main.py --date 2025-11-14 --auth-method manual
```

Debug mode with visible browser:
```bash
python main.py --log-level DEBUG
```

## Workflow

The module executes the following workflow:

1. **Read Bulletin** (Step 1/8)
   - Reads bulletin text from Module 02 output
   - Validates bulletin content

2. **Initialize Browser** (Step 2/8)
   - Starts Selenium WebDriver
   - Configures download settings

3. **Authenticate** (Step 3/8)
   - Logs into Google account (manual or cookies)
   - Verifies authentication success

4. **Open Colab Notebook** (Step 4/8)
   - Navigates to specified Colab URL
   - Waits for notebook to load

5. **Connect Runtime** (Step 5/8)
   - Connects to Colab runtime
   - Waits for GPU/TPU allocation

6. **Insert Text** (Step 6/8)
   - Modifies text input cell with bulletin content
   - Sets TTS generation parameters

7. **Execute Cells** (Step 7/8)
   - Executes notebook cells sequentially
   - Monitors generation progress
   - Waits for completion

8. **Download Audio** (Step 8/8)
   - Waits for audio file generation
   - Downloads to local output directory
   - Verifies file integrity

## Output

Generated audio files are saved to:
```
module_03/output/
├── 2025-11-11.wav
├── 2025-11-12.wav
├── 2025-11-13.wav
└── ...
```

Log files are saved to:
```
module_03/logs/
└── module_03_YYYYMMDD_HHMMSS.log
```

## Troubleshooting

### Authentication Issues
- **Cookie expired**: Re-export cookies from browser
- **Manual login fails**: Check Google security settings, may need to disable 2FA temporarily

### Runtime Connection Issues
- **Timeout**: Increase `COLAB_RUNTIME_CONNECT_TIMEOUT` in config
- **No GPU available**: Wait and retry, or use different Google account

### Cell Execution Issues
- **Cell index wrong**: Adjust cell indices in config to match your notebook
- **Generation timeout**: Increase `GENERATION_TIMEOUT` for longer bulletins

### Download Issues
- **File not found**: Ensure generation completed successfully
- **Download fails**: Check download directory permissions

### Browser Issues
- **WebDriver error**: Update chromedriver: `pip install --upgrade webdriver-manager`
- **Browser crash**: Disable headless mode for debugging: `--headless False`

## Dependencies

- **selenium**: Browser automation
- **webdriver-manager**: Automatic WebDriver management
- **python-dateutil**: Date parsing and manipulation

## Integration

### Input from Module 02
Reads bulletin text files from:
```
module_02/output/YYYY-MM-DD.txt
```

### Output for Downstream Use
Generated audio files can be used for:
- Broadcasting/streaming platforms
- Podcast distribution
- Audio archiving systems
- Accessibility applications

## Notes

- **Runtime Limits**: Google Colab has usage limits; monitor your usage
- **Generation Time**: Varies based on text length (typically 5-15 minutes)
- **Audio Quality**: Depends on TTS model and parameters configured
- **Network Stability**: Requires stable internet connection throughout process
- **Browser Resources**: May consume significant memory; close unused applications

## Future Enhancements

- [ ] Support for multiple TTS models
- [ ] Parallel processing for multiple bulletins
- [ ] Audio post-processing (normalization, compression)
- [ ] Integration with cloud storage (Google Drive, S3)
- [ ] Web interface for monitoring
- [ ] Email notifications on completion/failure
- [ ] Support for other Colab alternatives (Kaggle, Paperspace)

## License

Part of the ATI_02 project.
