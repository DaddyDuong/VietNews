"""
RSS feed fetcher
"""
import requests
from typing import Optional
from config import REQUEST_TIMEOUT, RETRY_ATTEMPTS, USER_AGENT
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RSSFetcher:
    """Handles fetching RSS feed content from URLs"""
    
    def __init__(self):
        self.timeout = REQUEST_TIMEOUT
        self.retry_attempts = RETRY_ATTEMPTS
        self.headers = {
            'User-Agent': USER_AGENT
        }
    
    def fetch(self, url: str) -> Optional[str]:
        """
        Fetch RSS feed content from URL
        
        Args:
            url: RSS feed URL
        
        Returns:
            RSS XML content as string, or None if failed
        """
        logger.info(f"Fetching RSS feed: {url}")
        
        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                logger.info(f"Successfully fetched RSS feed: {url}")
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt}/{self.retry_attempts} failed for {url}: {e}")
                
                if attempt == self.retry_attempts:
                    logger.error(f"Failed to fetch RSS feed after {self.retry_attempts} attempts: {url}")
                    return None
        
        return None
