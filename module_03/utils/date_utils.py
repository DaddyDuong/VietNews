"""
Date utility functions
"""
from datetime import datetime, timedelta
from typing import Optional


def get_yesterday() -> datetime:
    """
    Get yesterday's date
    
    Returns:
        Yesterday's datetime
    """
    return datetime.now() - timedelta(days=1)


def parse_date(date_str: str, format: str = "%Y-%m-%d") -> Optional[datetime]:
    """
    Parse date string
    
    Args:
        date_str: Date string to parse
        format: Date format
        
    Returns:
        Parsed datetime or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, format)
    except ValueError:
        return None


def format_date(date: datetime, format: str = "%Y-%m-%d") -> str:
    """
    Format datetime to string
    
    Args:
        date: Datetime to format
        format: Output format
        
    Returns:
        Formatted date string
    """
    return date.strftime(format)


def get_date_from_arg(date_arg: str) -> datetime:
    """
    Get datetime from command line argument
    
    Args:
        date_arg: Date argument ("yesterday", "YYYY-MM-DD", or "latest")
        
    Returns:
        Datetime object
        
    Raises:
        ValueError: If date argument is invalid
    """
    if date_arg.lower() == "yesterday":
        return get_yesterday()
    elif date_arg.lower() == "today":
        return datetime.now()
    elif date_arg.lower() == "latest":
        return datetime.now()  # Will be handled by bulletin reader
    else:
        # Try to parse as date
        parsed = parse_date(date_arg)
        if parsed:
            return parsed
        else:
            raise ValueError(f"Invalid date format: {date_arg}. Use 'yesterday', 'today', or 'YYYY-MM-DD'")


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"
