# Module 02: AI News Bulletin Generator

An intelligent news bulletin generation system powered by Google Gemini AI that transforms collected news articles into structured, broadcast-ready Vietnamese news bulletins.

## Overview

Module 02 processes news articles from the database (created by Module 01) and uses Google Gemini AI to:
- Cluster related articles by topic
- Identify and remove duplicate content
- Generate cohesive Vietnamese news bulletins
- Format text for Text-to-Speech (TTS) conversion
- Export bulletins in both JSON and TXT formats

## Features

### 🤖 AI-Powered Generation
- **Dual-stage processing**: Clustering + Synthesis for better quality
- **Gemini 2.5 Flash** with extended thinking for nuanced understanding
- **Automatic fallback** to Gemini 2.5 Flash Lite for stability
- **Structured output** with schema validation

### 📰 Smart Content Processing
- **Topic clustering**: Groups related articles automatically
- **Duplicate detection**: Removes redundant information
- **Priority scoring**: Ranks topics by importance (1-10)
- **Story selection**: Generates 3-5 stories per bulletin

### 🎙️ TTS-Ready Formatting
- Vietnamese text normalization
- Number-to-word conversion (e.g., "2025" → "hai không hai mươi lăm")
- Acronym expansion (e.g., "AI" → "ây-ai")
- Proper pronunciation guides

### ✅ Quality Validation
- Minimum article requirements
- Two-day fallback for sparse news days
- Comprehensive error handling
- Detailed logging

## Architecture

```
module_02/
├── main.py                    # Entry point & orchestration
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
│
├── database/
│   └── news_reader.py         # SQLite database interface
│
├── gemini_client/
│   ├── client.py              # Gemini API wrapper
│   ├── schemas.py             # JSON schemas for structured output
│   └── prompts.py             # System prompts & templates
│
├── processor/
│   ├── article_processor.py  # Article filtering & processing
│   ├── bulletin_generator.py # AI bulletin generation
│   └── text_formatter.py     # TTS text formatting
│
├── utils/
│   ├── date_utils.py          # Date handling utilities
│   ├── logger.py              # Logging configuration
│   └── validator.py           # Bulletin validation
│
└── output/                    # Generated bulletins
    ├── YYYY-MM-DD.json        # Structured bulletin data
    └── YYYY-MM-DD.txt         # TTS-ready text
```

## Installation

### Prerequisites
- Python 3.8+
- Google Gemini API key
- Module 01 database (news.db)

### Setup

1. **Install dependencies**:
```bash
cd module_02
pip install -r requirements.txt
```

2. **Configure API key**:

Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_api_key_here
```

Get your API key from: https://aistudio.google.com/apikey

3. **Verify database path**:

Ensure `NEWS_DB_PATH` in `config.py` points to Module 01's database:
```python
NEWS_DB_PATH = PROJECT_ROOT / "module_01" / "output" / "news.db"
```

## Usage

### Basic Usage

Generate bulletin for yesterday:
```bash
python main.py
```

### Advanced Options

Generate for specific date:
```bash
python main.py --date 2025-11-15
```

Regenerate existing bulletin:
```bash
python main.py --date 2025-11-15 --regenerate
```

## Configuration

Key settings in `config.py`:

### AI Model Settings
```python
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_FALLBACK_MODEL = "gemini-2.5-flash-lite"

GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}

THINKING_CONFIG = {
    "thinking_budget": 10000,  # Extended thinking tokens
    "include_thoughts": False,
}
```

### Content Parameters
```python
MIN_STORIES = 3              # Minimum stories per bulletin
MAX_STORIES = 5              # Maximum stories per bulletin
MIN_ARTICLES_REQUIRED = 5    # Minimum articles needed
FALLBACK_MIN_ARTICLES = 3    # Fallback minimum with 2-day window
```

### TTS Settings
```python
TTS_SETTINGS = {
    "convert_numbers": True,
    "expand_acronyms": True,
    "add_pronunciation_guides": True,
}
```

## Output Format

### JSON Output (`YYYY-MM-DD.json`)
```json
{
  "bulletin_date": "2025-11-15",
  "bulletin_date_vietnamese": "15 tháng 11 năm 2025",
  "stories": [
    {
      "title": "Story title",
      "content": "Story content...",
      "priority": 9,
      "category": "Category name",
      "source_articles": [1, 2, 3]
    }
  ],
  "metadata": {
    "total_stories": 5,
    "total_articles_used": 15,
    "generation_timestamp": "2025-11-16T10:30:00",
    "model_used": "gemini-2.5-flash"
  }
}
```

### TXT Output (`YYYY-MM-DD.txt`)
Vietnamese text ready for TTS conversion, with proper pronunciation:
```
Bản tin công nghệ ngày 15 tháng 11 năm hai không hai mươi lăm...
```

## Workflow

1. **Date Selection**: Defaults to yesterday or uses specified date
2. **Article Retrieval**: Fetches articles from database for target date
3. **Article Processing**: Filters and prepares articles
4. **AI Clustering**: Groups articles by topic, identifies duplicates
5. **Bulletin Generation**: Creates cohesive bulletin from clusters
6. **TTS Formatting**: Converts text for Vietnamese pronunciation
7. **Validation**: Ensures quality standards
8. **Export**: Saves JSON and TXT files

## Error Handling

### Automatic Fallbacks
- **Insufficient articles**: Extends window to 2 days
- **API errors**: Switches to fallback model
- **Generation failures**: Retries with exponential backoff

### Retry Configuration
```python
MAX_RETRIES = 3
RETRY_DELAY = 2           # seconds
RETRY_BACKOFF = 2         # multiplier
```

## Logging

Detailed logs track:
- Article retrieval and filtering
- AI generation process
- Token usage and costs
- Validation results
- File operations

Example output:
```
2025-11-16 10:30:00 - INFO - Target date: 2025-11-15
2025-11-16 10:30:05 - INFO - Retrieved 18 articles
2025-11-16 10:30:10 - INFO - Clustering complete: 7 topics, 3 duplicates
2025-11-16 10:30:25 - INFO - Generated 5 stories (total: 1,234 words)
2025-11-16 10:30:26 - SUCCESS - Bulletin saved
```

## Dependencies

- **google-genai** (>=0.4.0): Gemini API client
- **python-dotenv** (>=1.0.0): Environment variable management

## Integration with Other Modules

### Input
- Reads from: `module_01/output/news.db` (SQLite database)

### Output
- Writes to: `module_02/output/`
  - `YYYY-MM-DD.json`: Structured bulletin data
  - `YYYY-MM-DD.txt`: TTS-ready text

### Used by
- **Module 03**: Consumes TXT files for audio generation

## Best Practices

1. **API Key Security**: Never commit `.env` file to version control
2. **Database Path**: Ensure Module 01 has generated the database first
3. **Date Range**: Allow 24 hours after data collection before generating bulletins
4. **Token Budget**: Monitor Gemini API usage for cost control
5. **Output Verification**: Review generated bulletins for quality

## Troubleshooting

### No articles found
- Ensure Module 01 has collected articles for the target date
- Check database path in `config.py`

### API errors
- Verify `GEMINI_API_KEY` is set correctly
- Check API quota limits
- Review network connectivity

### Poor quality output
- Increase `thinking_budget` for more deliberation
- Adjust `temperature` (lower = more conservative)
- Ensure sufficient source articles (minimum 5)

## Contact

For issues or questions, please refer to the main project documentation.
