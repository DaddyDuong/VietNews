"""
Date utility functions
"""
from datetime import datetime, timedelta
from typing import Optional


def get_yesterday(reference_date: Optional[datetime] = None) -> datetime:
    """
    Get yesterday's date
    
    Args:
        reference_date: Reference date (defaults to today)
    
    Returns:
        Yesterday's datetime
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    return reference_date - timedelta(days=1)


def format_date_iso(date: datetime) -> str:
    """
    Format date as ISO string (YYYY-MM-DD)
    
    Args:
        date: Datetime object
    
    Returns:
        ISO formatted date string
    """
    return date.strftime("%Y-%m-%d")


def format_date_vietnamese(date: datetime) -> str:
    """
    Format date in Vietnamese style
    
    Args:
        date: Datetime object
    
    Returns:
        Vietnamese formatted date string (e.g., "15 tháng 11 năm 2025")
    """
    day = date.day
    month = date.month
    year = date.year
    
    return f"{day} tháng {month} năm {year}"


def format_date_vietnamese_full(date: datetime) -> str:
    """
    Format date in Vietnamese style with weekday
    
    Args:
        date: Datetime object
    
    Returns:
        Full Vietnamese date string (e.g., "Thứ Sáu, 15 tháng 11 năm 2025")
    """
    weekdays = {
        0: "Thứ Hai",
        1: "Thứ Ba",
        2: "Thứ Tư",
        3: "Thứ Năm",
        4: "Thứ Sáu",
        5: "Thứ Bảy",
        6: "Chủ Nhật",
    }
    
    weekday = weekdays[date.weekday()]
    date_str = format_date_vietnamese(date)
    
    return f"{weekday}, {date_str}"


def parse_date_iso(date_str: str) -> datetime:
    """
    Parse ISO date string to datetime
    
    Args:
        date_str: Date string in YYYY-MM-DD format
    
    Returns:
        Datetime object
    """
    return datetime.strptime(date_str, "%Y-%m-%d")


def get_date_range(
    end_date: Optional[datetime] = None,
    days: int = 1
) -> tuple[datetime, datetime]:
    """
    Get date range for the last N days
    
    Args:
        end_date: End date (defaults to yesterday)
        days: Number of days to go back
    
    Returns:
        Tuple of (start_date, end_date)
    """
    if end_date is None:
        end_date = get_yesterday()
    
    start_date = end_date - timedelta(days=days - 1)
    
    return start_date, end_date
