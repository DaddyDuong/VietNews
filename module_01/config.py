"""
Configuration for RSS parser and scraper module
"""
from datetime import datetime
import os

# Database configuration
DB_PATH = os.path.join("output", "news.db")

# RSS Feeds configuration
RSS_FEEDS = [
    {
        "url": "https://vnexpress.net/rss/so-hoa.rss",
        "name": "VnExpress - So Hoa",
        "identifier": "vnexpress_so_hoa"
    },
    {
        "url": "https://tuoitre.vn/rss/cong-nghe.rss",
        "name": "Tuoi Tre - Cong Nghe",
        "identifier": "tuoitre_cong_nghe"
    },
    {
        "url": "https://thanhnien.vn/rss/cong-nghe.rss",
        "name": "Thanh Nien - Cong Nghe",
        "identifier": "thanhnien_cong_nghe"
    },
    {
        "url": "https://dantri.com.vn/rss/cong-nghe.rss",
        "name": "Dan Tri - Cong Nghe",
        "identifier": "dantri_cong_nghe"
    },
    {
        "url": "https://vtv.vn/rss/cong-nghe.rss",
        "name": "VTV - Cong Nghe",
        "identifier": "vtv_cong_nghe"
    }
    # Add more RSS feeds here as needed
]

# Date range for initial run
START_DATE = "2025-11-11"  # YYYY-MM-DD format
# END_DATE will be current date/time

# Scraping settings
REQUEST_TIMEOUT = 30  # seconds
RETRY_ATTEMPTS = 3
DELAY_BETWEEN_REQUESTS = 1  # seconds
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# VnExpress specific content extraction
VNEXPRESS_SELECTORS = {
    "article_body": "article.fck_detail",
    "content": "p.Normal",
    "title": "h1.title-detail",
    "description": "p.description"
}

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
