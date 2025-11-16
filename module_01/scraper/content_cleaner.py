"""
Content cleaner for scraped articles
"""
import re
from typing import Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentCleaner:
    """Cleans scraped article content"""
    
    def __init__(self):
        # Patterns to remove
        self.noise_patterns = [
            r'Chia sẻ',
            r'Theo dõi',
            r'Like',
            r'Share',
            r'Comment',
            r'Bình luận',
            r'Xem thêm:',
            r'>>> Xem thêm:',
            r'\[.*?\]',  # Remove text in brackets
        ]
    
    def clean(self, content: str) -> Optional[str]:
        """
        Clean scraped content
        
        Args:
            content: Raw scraped content
        
        Returns:
            Cleaned content
        """
        if not content:
            return None
        
        # Handle special markers
        if content == "VIDEO_ARTICLE":
            logger.info("Video article marked - skipping cleaning")
            return "VIDEO_ARTICLE"
        
        try:
            # Remove noise patterns
            cleaned = content
            for pattern in self.noise_patterns:
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
            
            # Remove excessive whitespace
            cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Max 2 newlines
            cleaned = re.sub(r' +', ' ', cleaned)  # Single spaces
            
            # Remove leading/trailing whitespace
            cleaned = cleaned.strip()
            
            # Remove very short content (likely extraction errors)
            if len(cleaned) < 100:
                logger.warning("Content too short after cleaning")
                return None
            
            return cleaned
            
        except Exception as e:
            logger.error(f"Error cleaning content: {e}")
            return None
