# Module 01 - News Scraper

A Python-based news scraper module that collects technology news articles from Vietnamese news sources via RSS feeds and scrapes their full content.

## Overview

This module automates the process of:
1. Fetching RSS feeds from multiple Vietnamese news sources
2. Parsing and cleaning article metadata
3. Storing articles in a SQLite database
4. Scraping full article content from source websites
5. Cleaning and processing article content

## Features

- **Multi-source RSS aggregation**: Supports multiple Vietnamese news sources (VnExpress, Tuoi Tre, Thanh Nien, Dan Tri, VTV)
- **Duplicate detection**: Prevents duplicate articles using link-based deduplication
- **Robust scraping**: Includes retry logic, timeout handling, and error recovery
- **Content extraction**: Site-specific content extractors for better accuracy
- **Video article detection**: Automatically skips video-only articles
- **Batch processing**: Efficient batch insertion for better database performance
- **Comprehensive logging**: Detailed logging throughout the scraping workflow

## Project Structure

```
module_01/
├── __init__.py                 # Module initialization
├── config.py                   # Configuration settings and RSS feeds
├── main.py                     # Main orchestrator and entry point
├── database/
│   ├── __init__.py
│   ├── db_manager.py          # Database CRUD operations
│   └── schema.py              # Database schema definitions
├── rss_parser/
│   ├── __init__.py
│   ├── fetcher.py             # RSS feed fetching
│   ├── parser.py              # RSS feed parsing
│   └── cleaner.py             # Article metadata cleaning
├── scraper/
│   ├── __init__.py
│   ├── content_scraper.py     # Web scraping and content extraction
│   └── content_cleaner.py     # Content cleaning and normalization
└── utils/
    ├── __init__.py
    ├── date_utils.py          # Date parsing utilities
    └── logger.py              # Logging setup
```

## Database Schema

The module uses SQLite with the following schema:

```sql
news_articles:
  - id (INTEGER PRIMARY KEY)
  - title (TEXT NOT NULL)
  - description (TEXT)
  - content (TEXT)
  - rss (TEXT NOT NULL)
  - link (TEXT UNIQUE NOT NULL)
  - date (TEXT NOT NULL)
  - created_at (TEXT)
  - updated_at (TEXT)

Indexes:
  - idx_link (on link)
  - idx_date (on date)
  - idx_rss (on rss)
```

## Configuration

Edit `config.py` to customize:

### RSS Feeds
```python
RSS_FEEDS = [
    {
        "url": "https://vnexpress.net/rss/so-hoa.rss",
        "name": "VnExpress - So Hoa",
        "identifier": "vnexpress_so_hoa"
    },
    # Add more feeds...
]
```

### Scraping Settings
- `REQUEST_TIMEOUT`: HTTP request timeout (default: 30 seconds)
- `RETRY_ATTEMPTS`: Number of retry attempts (default: 3)
- `DELAY_BETWEEN_REQUESTS`: Delay between requests (default: 1 second)
- `USER_AGENT`: Browser user agent string
- `START_DATE`: Initial date for article collection (YYYY-MM-DD format)

### Database
- `DB_PATH`: SQLite database file path (default: "news.db")

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- `requests>=2.31.0` - HTTP library
- `feedparser>=6.0.10` - RSS feed parsing
- `beautifulsoup4>=4.12.2` - HTML parsing
- `html5lib>=1.1` - HTML5 parser

## Usage

### Basic Usage

Run the scraper module:
```bash
cd module_01
python main.py
```

### Workflow

The module executes in two phases:

**Phase 1: RSS Feed Processing**
- Fetches RSS feeds from configured sources
- Parses article metadata (title, description, link, date)
- Cleans and normalizes data
- Inserts new articles into database (skips duplicates)

**Phase 2: Content Scraping**
- Retrieves articles without full content
- Scrapes article HTML from source websites
- Extracts main content using site-specific selectors
- Cleans and processes content
- Updates database with scraped content

### Programmatic Usage

```python
from module_01.main import NewsScraperModule

# Initialize and run
scraper = NewsScraperModule()
scraper.run()
```

## Components

### Database Manager (`database/db_manager.py`)
Handles all database operations:
- `insert_article()` - Insert single article
- `insert_articles_batch()` - Batch insert for efficiency
- `get_articles_without_content()` - Retrieve articles needing content
- `update_article_content()` - Update article content
- `link_exists()` - Check for duplicates

### RSS Fetcher (`rss_parser/fetcher.py`)
- Fetches RSS feed content with retry logic
- Configurable timeout and headers
- Error handling and logging

### RSS Parser (`rss_parser/parser.py`)
- Parses RSS XML using feedparser
- Extracts article metadata
- Handles date parsing and normalization

### Content Scraper (`scraper/content_scraper.py`)
- Scrapes article HTML
- Site-specific content extraction (VnExpress, Tuoi Tre, etc.)
- Video article detection
- Configurable selectors for each news source

### Content Cleaner (`scraper/content_cleaner.py`)
- Removes HTML tags and formatting
- Normalizes whitespace
- Cleans special characters
- Formats content for storage

## Supported News Sources

Currently configured for Vietnamese technology news:

1. **VnExpress** - So Hoa (Digital/Tech)
2. **Tuoi Tre** - Cong Nghe (Technology)
3. **Thanh Nien** - Cong Nghe (Technology)
4. **Dan Tri** - Cong Nghe (Technology)
5. **VTV** - Cong Nghe (Technology)

## Error Handling

- Retry mechanism for network failures
- Graceful handling of parsing errors
- Video article detection and skipping
- Comprehensive error logging
- Database transaction rollback on errors

## Logging

Logs are output to console with detailed information:
- INFO: Normal operations and progress
- WARNING: Non-critical issues (e.g., no articles found)
- ERROR: Failed operations (e.g., network errors, parsing failures)

## Output

After execution, the module displays:
- Number of new articles added from RSS feeds
- Number of articles successfully scraped
- Summary statistics and completion status

Database file `news.db` will be created in the module directory containing all scraped articles.

## Notes

- The module automatically skips duplicate articles based on link
- Video-only articles are marked and skipped during content scraping
- Date filtering uses `START_DATE` from config for initial runs
- Database uses SQLite for simplicity and portability

## Future Enhancements

Potential improvements:
- Add more news sources
- Implement incremental updates
- Add full-text search capabilities
- Export to different formats (JSON, CSV)
- Add scheduling/cron support
- Implement content summarization
