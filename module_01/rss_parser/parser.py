"""
RSS feed parser
"""
import feedparser
from typing import List, Dict, Optional
from utils.logger import setup_logger
from utils.date_utils import parse_rss_date, normalize_date, is_within_date_range
from config import START_DATE

logger = setup_logger(__name__)


class RSSParser:
    """Parses RSS feed XML and extracts article data"""
    
    def __init__(self):
        pass
    
    def parse(self, rss_content: str, rss_identifier: str, rss_name: str) -> List[Dict]:
        """
        Parse RSS feed content and extract articles
        
        Args:
            rss_content: RSS XML content as string
            rss_identifier: Unique identifier for this RSS feed
            rss_name: Human-readable name of RSS feed
        
        Returns:
            List of article dictionaries
        """
        logger.info(f"Parsing RSS feed: {rss_name}")
        
        try:
            feed = feedparser.parse(rss_content)
            
            if feed.bozo:
                logger.warning(f"RSS feed has parsing issues: {feed.bozo_exception}")
            
            articles = []
            
            for entry in feed.entries:
                article = self._extract_article_data(entry, rss_identifier, rss_name)
                if article:
                    articles.append(article)
            
            logger.info(f"Parsed {len(articles)} articles from {rss_name}")
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing RSS feed {rss_name}: {e}")
            return []
    
    def _extract_article_data(self, entry, rss_identifier: str, rss_name: str) -> Optional[Dict]:
        """
        Extract data from a single RSS entry
        
        Args:
            entry: feedparser entry object
            rss_identifier: RSS feed identifier
            rss_name: RSS feed name
        
        Returns:
            Article dictionary or None if invalid
        """
        try:
            # Extract title
            title = entry.get('title', '').strip()
            if not title:
                logger.debug("Skipping entry without title")
                return None
            
            # Extract link
            link = entry.get('link', '').strip()
            if not link:
                logger.debug(f"Skipping entry without link: {title}")
                return None
            
            # Extract description/summary
            description = entry.get('description', '') or entry.get('summary', '')
            
            # Extract and parse date
            date_str = entry.get('published', '') or entry.get('updated', '')
            if not date_str:
                logger.warning(f"No date found for article: {title}")
                return None
            
            date_obj = parse_rss_date(date_str)
            if not date_obj:
                logger.warning(f"Could not parse date for article: {title}")
                return None
            
            # Filter by date range
            if not is_within_date_range(date_obj, START_DATE):
                logger.debug(f"Article outside date range: {title} ({date_obj})")
                return None
            
            normalized_date = normalize_date(date_obj)
            
            return {
                'title': title,
                'description': description,
                'link': link,
                'rss': rss_identifier,
                'date': normalized_date
            }
            
        except Exception as e:
            logger.error(f"Error extracting article data: {e}")
            return None
