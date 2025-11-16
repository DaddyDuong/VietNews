"""
News database reader for accessing articles from module_01's news.db
"""
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from contextlib import contextmanager
from pathlib import Path


class NewsReader:
    """Reads news articles from the module_01 database"""
    
    def __init__(self, db_path: Path):
        """
        Initialize news reader
        
        Args:
            db_path: Path to the news.db database file
        """
        self.db_path = db_path
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"Database not found at {db_path}. "
                "Please ensure module_01 has been run first."
            )
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def get_articles_by_date(
        self, 
        target_date: str,
        min_content_length: int = 100
    ) -> List[Dict]:
        """
        Get all articles from a specific date
        
        Args:
            target_date: Date in YYYY-MM-DD format
            min_content_length: Minimum content length to include
        
        Returns:
            List of article dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Query articles from target date with valid content
            cursor.execute("""
                SELECT 
                    id,
                    title,
                    description,
                    content,
                    rss,
                    link,
                    date,
                    created_at
                FROM news_articles
                WHERE date LIKE ? || '%'
                  AND content IS NOT NULL
                  AND content != 'VIDEO_ARTICLE'
                  AND LENGTH(content) >= ?
                ORDER BY date DESC
            """, (target_date, min_content_length))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_articles_yesterday(
        self, 
        reference_date: Optional[datetime] = None,
        min_content_length: int = 100
    ) -> List[Dict]:
        """
        Get all articles from yesterday
        
        Args:
            reference_date: Reference date (defaults to today)
            min_content_length: Minimum content length to include
        
        Returns:
            List of article dictionaries
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        yesterday = reference_date - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        
        return self.get_articles_by_date(yesterday_str, min_content_length)
    
    def get_articles_date_range(
        self,
        start_date: str,
        end_date: str,
        min_content_length: int = 100
    ) -> List[Dict]:
        """
        Get articles within a date range
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            min_content_length: Minimum content length to include
        
        Returns:
            List of article dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id,
                    title,
                    description,
                    content,
                    rss,
                    link,
                    date,
                    created_at
                FROM news_articles
                WHERE date >= ? AND date < ? || ' 23:59:59'
                  AND content IS NOT NULL
                  AND content != 'VIDEO_ARTICLE'
                  AND LENGTH(content) >= ?
                ORDER BY date DESC
            """, (start_date, end_date, min_content_length))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_articles_last_n_days(
        self,
        n_days: int = 2,
        reference_date: Optional[datetime] = None,
        min_content_length: int = 100
    ) -> List[Dict]:
        """
        Get articles from the last N days
        
        Args:
            n_days: Number of days to look back
            reference_date: Reference date (defaults to today)
            min_content_length: Minimum content length to include
        
        Returns:
            List of article dictionaries
        """
        if reference_date is None:
            reference_date = datetime.now()
        
        end_date = reference_date - timedelta(days=1)
        start_date = end_date - timedelta(days=n_days - 1)
        
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        return self.get_articles_date_range(start_str, end_str, min_content_length)
    
    def get_article_count(self, target_date: str) -> int:
        """
        Get count of articles for a specific date
        
        Args:
            target_date: Date in YYYY-MM-DD format
        
        Returns:
            Number of articles
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM news_articles
                WHERE date LIKE ? || '%'
                  AND content IS NOT NULL
                  AND content != 'VIDEO_ARTICLE'
            """, (target_date,))
            
            return cursor.fetchone()[0]
    
    def get_sources_summary(self, articles: List[Dict]) -> Dict[str, int]:
        """
        Get summary of article sources
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            Dictionary mapping source to count
        """
        sources = {}
        for article in articles:
            rss = article.get('rss', 'unknown')
            sources[rss] = sources.get(rss, 0) + 1
        return sources
