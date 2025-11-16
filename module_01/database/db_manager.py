"""
Database manager for CRUD operations
"""
import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
from database.schema import ALL_SCHEMA_COMMANDS
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseManager:
    """Manages all database operations for news articles"""
    
    def __init__(self, db_path: str):
        """
        Initialize database manager
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._initialize_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Create tables and indexes if they don't exist"""
        logger.info(f"Initializing database at {self.db_path}")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for command in ALL_SCHEMA_COMMANDS:
                cursor.execute(command)
        
        logger.info("Database initialized successfully")
    
    def link_exists(self, link: str) -> bool:
        """
        Check if a news article link already exists in database
        
        Args:
            link: Article URL
        
        Returns:
            True if link exists
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM news_articles WHERE link = ? LIMIT 1", (link,))
            return cursor.fetchone() is not None
    
    def insert_article(self, article: Dict) -> Optional[int]:
        """
        Insert a single news article
        
        Args:
            article: Dictionary with keys: title, description, link, rss, date
        
        Returns:
            Article ID if inserted, None if duplicate
        """
        if self.link_exists(article['link']):
            logger.debug(f"Article already exists: {article['link']}")
            return None
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO news_articles (title, description, content, rss, link, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                article['title'],
                article.get('description', ''),
                None,  # content will be scraped later
                article['rss'],
                article['link'],
                article['date']
            ))
            
            article_id = cursor.lastrowid
            logger.info(f"Inserted article: {article['title'][:50]}... (ID: {article_id})")
            return article_id
    
    def insert_articles_batch(self, articles: List[Dict]) -> int:
        """
        Insert multiple articles in a single transaction
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            Number of articles inserted
        """
        inserted_count = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for article in articles:
                # Check for duplicates
                cursor.execute("SELECT 1 FROM news_articles WHERE link = ? LIMIT 1", (article['link'],))
                if cursor.fetchone() is not None:
                    logger.debug(f"Skipping duplicate: {article['link']}")
                    continue
                
                cursor.execute("""
                    INSERT INTO news_articles (title, description, content, rss, link, date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    article['title'],
                    article.get('description', ''),
                    None,
                    article['rss'],
                    article['link'],
                    article['date']
                ))
                inserted_count += 1
        
        logger.info(f"Batch insert: {inserted_count} articles added")
        return inserted_count
    
    def get_articles_without_content(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Get articles that need content scraping (content is NULL)
        
        Args:
            limit: Maximum number of articles to return
        
        Returns:
            List of article dictionaries
        """
        query = "SELECT * FROM news_articles WHERE content IS NULL"
        if limit:
            query += f" LIMIT {limit}"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def update_article_content(self, article_id: int, content: str) -> bool:
        """
        Update article content after scraping
        
        Args:
            article_id: Article ID
            content: Scraped and cleaned content
        
        Returns:
            True if updated successfully
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE news_articles 
                SET content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (content, article_id))
            
            success = cursor.rowcount > 0
            if success:
                logger.info(f"Updated content for article ID: {article_id}")
            return success
    
    def get_article_count(self) -> int:
        """Get total number of articles in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            return cursor.fetchone()[0]
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM news_articles")
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM news_articles WHERE content IS NOT NULL AND content != 'VIDEO_ARTICLE'")
            with_content = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM news_articles WHERE content IS NULL")
            without_content = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM news_articles WHERE content = 'VIDEO_ARTICLE'")
            video_articles = cursor.fetchone()[0]
            
            return {
                "total_articles": total,
                "with_content": with_content,
                "without_content": without_content,
                "video_articles": video_articles
            }
