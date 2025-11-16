"""
Main entry point for the news scraper module
"""
import os
import sys
from typing import List, Dict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DB_PATH, RSS_FEEDS
from database.db_manager import DatabaseManager
from rss_parser.fetcher import RSSFetcher
from rss_parser.parser import RSSParser
from rss_parser.cleaner import RSSCleaner
from scraper.content_scraper import ContentScraper
from scraper.content_cleaner import ContentCleaner
from utils.logger import setup_logger

logger = setup_logger(__name__)


class NewsScraperModule:
    """Main orchestrator for the news scraping workflow"""
    
    def __init__(self):
        # Get absolute path for database
        db_path = os.path.join(os.path.dirname(__file__), DB_PATH)
        
        # Initialize components
        self.db = DatabaseManager(db_path)
        self.rss_fetcher = RSSFetcher()
        self.rss_parser = RSSParser()
        self.rss_cleaner = RSSCleaner()
        self.content_scraper = ContentScraper()
        self.content_cleaner = ContentCleaner()
    
    def run(self):
        """Execute the complete scraping workflow"""
        logger.info("=" * 60)
        logger.info("Starting News Scraper Module")
        logger.info("=" * 60)
        
        # Phase 1: Process RSS feeds
        logger.info("\n--- Phase 1: Processing RSS Feeds ---")
        total_new_articles = self.process_rss_feeds()
        
        # Phase 2: Scrape article content
        logger.info("\n--- Phase 2: Scraping Article Content ---")
        total_scraped = self.scrape_article_contents()
        
        # Print summary
        self.print_summary(total_new_articles, total_scraped)
        
        logger.info("\n" + "=" * 60)
        logger.info("News Scraper Module Completed")
        logger.info("=" * 60)
    
    def process_rss_feeds(self) -> int:
        """
        Process all RSS feeds and insert articles into database
        
        Returns:
            Total number of new articles added
        """
        total_added = 0
        
        for feed_config in RSS_FEEDS:
            url = feed_config['url']
            name = feed_config['name']
            identifier = feed_config['identifier']
            
            logger.info(f"\nProcessing feed: {name}")
            logger.info(f"URL: {url}")
            
            # Fetch RSS content
            rss_content = self.rss_fetcher.fetch(url)
            if not rss_content:
                logger.error(f"Failed to fetch RSS feed: {name}")
                continue
            
            # Parse RSS
            articles = self.rss_parser.parse(rss_content, identifier, name)
            if not articles:
                logger.warning(f"No articles found in feed: {name}")
                continue
            
            # Clean articles
            cleaned_articles = [self.rss_cleaner.clean_article(article) for article in articles]
            
            # Insert into database
            count = self.db.insert_articles_batch(cleaned_articles)
            total_added += count
            
            logger.info(f"Added {count} new articles from {name}")
        
        return total_added
    
    def scrape_article_contents(self) -> int:
        """
        Scrape content for articles that don't have it yet
        
        Returns:
            Number of articles successfully scraped
        """
        # Get articles without content
        articles = self.db.get_articles_without_content()
        
        if not articles:
            logger.info("No articles need content scraping")
            return 0
        
        logger.info(f"Found {len(articles)} articles to scrape")
        
        scraped_count = 0
        failed_count = 0
        skipped_count = 0
        
        for i, article in enumerate(articles, 1):
            article_id = article['id']
            link = article['link']
            title = article['title']
            
            logger.info(f"\n[{i}/{len(articles)}] Scraping: {title[:60]}...")
            
            # Scrape HTML
            html = self.content_scraper.scrape(link)
            if not html:
                logger.error(f"Failed to scrape article {article_id}")
                failed_count += 1
                continue
            
            # Extract content (site-specific)
            content = self.content_scraper.extract_content(link, html)
            if not content:
                logger.error(f"Failed to extract content from article {article_id}")
                failed_count += 1
                continue
            
            # Check if it's a video article
            if content == "VIDEO_ARTICLE":
                logger.info(f"Skipping video article {article_id}")
                # Update with special marker so we don't try again
                self.db.update_article_content(article_id, "VIDEO_ARTICLE")
                skipped_count += 1
                continue
            
            # Clean content
            cleaned_content = self.content_cleaner.clean(content)
            if not cleaned_content:
                logger.error(f"Content cleaning failed for article {article_id}")
                failed_count += 1
                continue
            
            # Update database
            if self.db.update_article_content(article_id, cleaned_content):
                scraped_count += 1
                logger.info(f"Successfully scraped article {article_id}")
            else:
                failed_count += 1
                logger.error(f"Failed to update article {article_id}")
        
        logger.info(f"\nScraping complete: {scraped_count} successful, {skipped_count} video articles skipped, {failed_count} failed")
        return scraped_count
    
    def print_summary(self, new_articles: int, scraped_articles: int):
        """Print execution summary"""
        stats = self.db.get_stats()
        
        logger.info("\n" + "=" * 60)
        logger.info("EXECUTION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"New articles added:          {new_articles}")
        logger.info(f"Articles scraped:            {scraped_articles}")
        logger.info(f"\nDatabase Statistics:")
        logger.info(f"Total articles:              {stats['total_articles']}")
        logger.info(f"With content:                {stats['with_content']}")
        logger.info(f"Video articles (skipped):    {stats['video_articles']}")
        logger.info(f"Without content:             {stats['without_content']}")
        logger.info("=" * 60)


def main():
    """Entry point"""
    try:
        scraper = NewsScraperModule()
        scraper.run()
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
