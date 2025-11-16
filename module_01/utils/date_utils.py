"""
Date parsing and normalization utilities
"""
from datetime import datetime
from typing import Optional
import email.utils
from utils.logger import setup_logger

logger = setup_logger(__name__)


def parse_rss_date(date_string: str) -> Optional[datetime]:
    """
    Parse various RSS date formats to datetime object
    
    Common formats:
    - RFC 2822: "Mon, 13 Nov 2025 10:30:00 +0700"
    - ISO 8601: "2025-11-13T10:30:00+07:00"
    
    Args:
        date_string: Date string from RSS feed
    
    Returns:
        datetime object or None if parsing fails
    """
    if not date_string:
        return None
    
    try:
        # Try RFC 2822 format (common in RSS feeds)
        parsed_tuple = email.utils.parsedate_to_datetime(date_string)
        return parsed_tuple
    except Exception as e:
        logger.debug(f"RFC 2822 parsing failed for '{date_string}': {e}")
    
    # Try ISO 8601 format
    iso_formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    
    for fmt in iso_formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    logger.warning(f"Could not parse date: {date_string}")
    return None


def normalize_date(dt: datetime) -> str:
    """
    Normalize datetime to ISO 8601 string format
    
    Args:
        dt: datetime object
    
    Returns:
        ISO 8601 formatted string: "YYYY-MM-DD HH:MM:SS"
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def is_within_date_range(date: datetime, start_date: str) -> bool:
    """
    Check if date is within range (from start_date to now)
    
    Args:
        date: datetime object to check
        start_date: Start date string in YYYY-MM-DD format
    
    Returns:
        True if date is within range
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        now = datetime.now()
        
        # Make dates timezone-naive for comparison if needed
        if date.tzinfo is not None:
            date = date.replace(tzinfo=None)
        if start.tzinfo is not None:
            start = start.replace(tzinfo=None)
        
        return start <= date <= now
    except Exception as e:
        logger.error(f"Error checking date range: {e}")
        return False
