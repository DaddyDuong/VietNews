"""
RSS data cleaner
"""
import re
import html
from typing import Dict
from utils.logger import setup_logger

logger = setup_logger(__name__)


class RSSCleaner:
    """Cleans and normalizes RSS feed data"""
    
    def __init__(self):
        pass
    
    def clean_article(self, article: Dict) -> Dict:
        """
        Clean and normalize article data from RSS
        
        Args:
            article: Raw article dictionary
        
        Returns:
            Cleaned article dictionary
        """
        cleaned = article.copy()
        
        # Clean title
        if 'title' in cleaned:
            cleaned['title'] = self._clean_text(cleaned['title'])
        
        # Clean description
        if 'description' in cleaned and cleaned['description']:
            cleaned['description'] = self._clean_html(cleaned['description'])
        
        # Clean link (normalize)
        if 'link' in cleaned:
            cleaned['link'] = cleaned['link'].strip()
        
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """
        Clean plain text
        
        Args:
            text: Text to clean
        
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _clean_html(self, html_text: str) -> str:
        """
        Remove HTML tags and clean text content
        
        Args:
            html_text: Text with HTML tags
        
        Returns:
            Plain text without HTML
        """
        if not html_text:
            return ""
        
        # Decode HTML entities first
        text = html.unescape(html_text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
