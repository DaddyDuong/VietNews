"""
Main entry point for AI News Bulletin Generator (Module 02)
"""
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta

# Add module to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_FALLBACK_MODEL,
    GENERATION_CONFIG,
    THINKING_CONFIG,
    NEWS_DB_PATH,
    OUTPUT_DIR,
    MIN_STORIES,
    MAX_STORIES,
    MIN_ARTICLES_REQUIRED,
    FALLBACK_TO_TWO_DAYS,
    FALLBACK_MIN_ARTICLES,
    TTS_SETTINGS,
    MAX_RETRIES,
    RETRY_DELAY,
    RETRY_BACKOFF,
)

from database.news_reader import NewsReader
from gemini_client.client import GeminiClient
from processor.article_processor import ArticleProcessor
from processor.bulletin_generator import BulletinGenerator
from processor.text_formatter import TTSFormatter
from utils.date_utils import (
    get_yesterday,
    format_date_iso,
    format_date_vietnamese,
)
from utils.logger import setup_logger
from utils.validator import BulletinValidator

logger = setup_logger(__name__)


class NewsBulletinModule:
    """Main orchestrator for news bulletin generation"""
    
    def __init__(self):
        """Initialize the bulletin generator module"""
        logger.info("Initializing News Bulletin Module")
        
        # Initialize components
        self.news_reader = NewsReader(NEWS_DB_PATH)
        self.article_processor = ArticleProcessor()
        self.tts_formatter = TTSFormatter()
        self.validator = BulletinValidator()
        
        # Initialize Gemini client
        self.gemini_client = GeminiClient(
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL,
            fallback_model=GEMINI_FALLBACK_MODEL,
            generation_config=GENERATION_CONFIG,
            thinking_config=THINKING_CONFIG,
            max_retries=MAX_RETRIES,
            retry_delay=RETRY_DELAY,
            retry_backoff=RETRY_BACKOFF,
        )
        
        self.bulletin_generator = BulletinGenerator(self.gemini_client)
        
        logger.info(f"Using model: {GEMINI_MODEL}")
        logger.info(f"Database: {NEWS_DB_PATH}")
        logger.info(f"Output directory: {OUTPUT_DIR}")
    
    def run(self, target_date: datetime = None, use_two_stage: bool = True):
        """
        Execute the complete bulletin generation workflow
        
        Args:
            target_date: Target date for bulletin (defaults to yesterday)
            use_two_stage: Whether to use two-stage generation (clustering + synthesis)
        """
        logger.info("=" * 70)
        logger.info("STARTING NEWS BULLETIN GENERATION")
        logger.info("=" * 70)
        
        # Step 1: Determine target date
        if target_date is None:
            target_date = get_yesterday()
        
        date_iso = format_date_iso(target_date)
        date_viet = format_date_vietnamese(target_date)
        
        logger.info(f"\nTarget date: {date_iso} ({date_viet})")
        
        # Step 2: Retrieve articles
        logger.info("\n--- Step 1: Retrieving Articles ---")
        articles = self._retrieve_articles(target_date)
        
        if not articles:
            logger.error("No articles found. Exiting.")
            return
        
        # Step 3: Process articles
        logger.info("\n--- Step 2: Processing Articles ---")
        processed_articles = self._process_articles(articles)
        
        # Step 4: Generate bulletin
        logger.info("\n--- Step 3: Generating Bulletin with AI ---")
        bulletin_data = self._generate_bulletin(
            processed_articles,
            date_viet,
            use_two_stage=use_two_stage
        )
        
        if not bulletin_data:
            logger.error("Failed to generate bulletin. Exiting.")
            return
        
        # Step 5: Format for TTS
        logger.info("\n--- Step 4: Formatting for TTS ---")
        tts_text = self._format_for_tts(bulletin_data)
        
        # Step 6: Validate output
        logger.info("\n--- Step 5: Validating Output ---")
        validation_result = self._validate_output(bulletin_data, tts_text)
        
        # Step 7: Save output
        logger.info("\n--- Step 6: Saving Output ---")
        self._save_output(date_iso, bulletin_data, tts_text, validation_result)
        
        # Step 8: Print summary
        self._print_summary(bulletin_data, validation_result)
        
        logger.info("\n" + "=" * 70)
        logger.info("BULLETIN GENERATION COMPLETED")
        logger.info("=" * 70)
    
    def _retrieve_articles(self, target_date: datetime) -> list:
        """Retrieve articles from database"""
        date_iso = format_date_iso(target_date)
        
        # Try getting articles from target date
        articles = self.news_reader.get_articles_yesterday(
            reference_date=target_date + timedelta(days=1)
        )
        
        logger.info(f"Found {len(articles)} articles from {date_iso}")
        
        # Fallback to last 2 days if not enough articles
        if len(articles) < MIN_ARTICLES_REQUIRED and FALLBACK_TO_TWO_DAYS:
            logger.warning(
                f"Only {len(articles)} articles found (minimum: {MIN_ARTICLES_REQUIRED}). "
                "Falling back to last 2 days..."
            )
            
            articles = self.news_reader.get_articles_last_n_days(
                n_days=2,
                reference_date=target_date + timedelta(days=1)
            )
            
            logger.info(f"Retrieved {len(articles)} articles from last 2 days")
            
            if len(articles) < FALLBACK_MIN_ARTICLES:
                logger.error(
                    f"Still not enough articles ({len(articles)} < {FALLBACK_MIN_ARTICLES})"
                )
                return []
        
        # Show source distribution
        sources = self.news_reader.get_sources_summary(articles)
        logger.info(f"Source distribution: {sources}")
        
        return articles
    
    def _process_articles(self, articles: list) -> list:
        """Process and clean articles"""
        logger.info(f"Processing {len(articles)} articles...")
        
        # Clean and process
        processed = self.article_processor.process_articles(articles)
        
        # Deduplicate
        processed = self.article_processor.deduplicate_articles(processed)
        logger.info(f"After deduplication: {len(processed)} articles")
        
        # Filter by length
        processed = self.article_processor.filter_by_length(processed)
        logger.info(f"After length filtering: {len(processed)} articles")
        
        return processed
    
    def _generate_bulletin(
        self,
        articles: list,
        date_viet: str,
        use_two_stage: bool = True
    ) -> dict:
        """Generate bulletin using AI"""
        logger.info(f"Generating bulletin from {len(articles)} articles...")
        logger.info(f"Using {'two-stage' if use_two_stage else 'single-stage'} generation")
        
        try:
            if use_two_stage:
                # Two-stage: clustering + synthesis
                result = self.bulletin_generator.generate_bulletin_two_stage(
                    articles=articles,
                    date_vietnamese=date_viet,
                    min_stories=MIN_STORIES,
                    max_stories=MAX_STORIES,
                    include_thoughts=True
                )
                
                # Log token usage
                usage = result.get("total_usage", {})
                logger.info(
                    f"Token usage - "
                    f"Prompt: {usage.get('prompt_tokens', 0)}, "
                    f"Output: {usage.get('output_tokens', 0)}, "
                    f"Thinking: {usage.get('thinking_tokens', 0)}"
                )
                
                return result
            else:
                # Single-stage: direct generation
                result = self.bulletin_generator.generate_bulletin(
                    articles=articles,
                    date_vietnamese=date_viet,
                    min_stories=MIN_STORIES,
                    max_stories=MAX_STORIES,
                    include_thoughts=True
                )
                
                # Log token usage
                usage = result.get("usage", {})
                logger.info(
                    f"Token usage - "
                    f"Prompt: {usage.get('prompt_token_count', 0)}, "
                    f"Output: {usage.get('candidates_token_count', 0)}, "
                    f"Thinking: {usage.get('thoughts_token_count', 0)}"
                )
                
                return {"bulletin": result["result"], "bulletin_usage": usage}
                
        except Exception as e:
            logger.error(f"Error generating bulletin: {e}", exc_info=True)
            return None
    
    def _format_for_tts(self, bulletin_data: dict) -> str:
        """Format bulletin text for TTS"""
        bulletin = bulletin_data.get("bulletin", {})
        full_bulletin = bulletin.get("full_bulletin", "")
        
        if not full_bulletin:
            logger.error("No full_bulletin text found in result")
            return ""
        
        logger.info(f"Formatting {len(full_bulletin)} characters for TTS...")
        
        # Format for TTS
        tts_text = self.tts_formatter.format_bulletin(
            full_bulletin,
            add_intro=TTS_SETTINGS.get("add_intro", True),
            add_outro=TTS_SETTINGS.get("add_outro", True)
        )
        
        logger.info(f"Formatted text length: {len(tts_text)} characters")
        
        return tts_text
    
    def _validate_output(self, bulletin_data: dict, tts_text: str) -> dict:
        """Validate output quality"""
        bulletin = bulletin_data.get("bulletin", {})
        
        validation = self.validator.validate_complete(bulletin, tts_text)
        
        if validation["is_valid"]:
            logger.info("✓ Validation passed")
        else:
            logger.warning("⚠ Validation issues found:")
            
            for error in validation["errors"]:
                logger.warning(f"  ERROR: {error}")
            
            for warning in validation["warnings"]:
                logger.warning(f"  WARNING: {warning}")
        
        return validation
    
    def _save_output(
        self,
        date_iso: str,
        bulletin_data: dict,
        tts_text: str,
        validation: dict
    ):
        """Save bulletin output to files"""
        # File paths
        txt_path = OUTPUT_DIR / f"{date_iso}.txt"
        json_path = OUTPUT_DIR / f"{date_iso}.json"
        
        # Save TTS text file
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(tts_text)
        logger.info(f"✓ Saved TTS text: {txt_path}")
        
        # Prepare metadata
        metadata = {
            "date": date_iso,
            "generated_at": datetime.now().isoformat(),
            "bulletin": bulletin_data.get("bulletin", {}),
            "validation": validation,
            "token_usage": bulletin_data.get("total_usage") or bulletin_data.get("bulletin_usage"),
        }
        
        # Include clustering info if available
        if "clustering" in bulletin_data:
            metadata["clustering"] = bulletin_data["clustering"]
        
        # Save JSON metadata
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ Saved metadata: {json_path}")
    
    def _print_summary(self, bulletin_data: dict, validation: dict):
        """Print execution summary"""
        bulletin = bulletin_data.get("bulletin", {})
        
        logger.info("\n" + "=" * 70)
        logger.info("SUMMARY")
        logger.info("=" * 70)
        
        logger.info(f"Date: {bulletin.get('bulletin_date', 'N/A')}")
        logger.info(f"Articles processed: {bulletin.get('total_articles_processed', 0)}")
        logger.info(f"Stories generated: {len(bulletin.get('stories', []))}")
        logger.info(f"Validation: {'✓ PASSED' if validation['is_valid'] else '⚠ ISSUES FOUND'}")
        
        # Show story topics
        stories = bulletin.get("stories", [])
        if stories:
            logger.info("\nStory topics:")
            for i, story in enumerate(stories, 1):
                priority = story.get("priority", 0)
                topic = story.get("topic", "Unknown")
                logger.info(f"  {i}. [{priority}/10] {topic}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Generate AI News Bulletin")
    parser.add_argument(
        "--date",
        type=str,
        help="Target date in YYYY-MM-DD format (defaults to yesterday)"
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Regenerate bulletin for the specified date"
    )
    
    args = parser.parse_args()
    
    # Parse target date
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            logger.error(f"Invalid date format: {args.date}. Use YYYY-MM-DD")
            sys.exit(1)
    
    try:
        module = NewsBulletinModule()
        module.run(target_date=target_date, use_two_stage=True)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
