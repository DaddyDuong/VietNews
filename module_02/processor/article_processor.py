"""
Article preprocessor for cleaning and preparing articles for AI processing
"""
import re
from typing import List, Dict


class ArticleProcessor:
    """Preprocesses articles before sending to AI"""
    
    @staticmethod
    def clean_content(content: str) -> str:
        """
        Clean article content
        
        Args:
            content: Raw article content
        
        Returns:
            Cleaned content
        """
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove URLs
        content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
        
        # Remove email addresses
        content = re.sub(r'\S+@\S+', '', content)
        
        # Remove excessive punctuation
        content = re.sub(r'\.{3,}', '...', content)
        content = re.sub(r'-{3,}', '---', content)
        
        # Trim
        content = content.strip()
        
        return content
    
    @staticmethod
    def truncate_content(content: str, max_length: int = 2000) -> str:
        """
        Truncate content to max length while preserving sentence boundaries
        
        Args:
            content: Article content
            max_length: Maximum length
        
        Returns:
            Truncated content
        """
        if len(content) <= max_length:
            return content
        
        # Find last sentence boundary before max_length
        truncated = content[:max_length]
        
        # Look for last period, exclamation, or question mark
        last_punct = max(
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )
        
        if last_punct > max_length * 0.7:  # At least 70% of desired length
            return truncated[:last_punct + 1]
        
        # No good boundary found, just truncate
        return truncated + "..."
    
    def process_article(self, article: Dict) -> Dict:
        """
        Process a single article
        
        Args:
            article: Article dictionary
        
        Returns:
            Processed article dictionary
        """
        processed = article.copy()
        
        # Clean content
        if 'content' in processed:
            processed['content'] = self.clean_content(processed['content'])
            processed['content'] = self.truncate_content(processed['content'])
        
        # Clean title
        if 'title' in processed:
            processed['title'] = self.clean_content(processed['title'])
        
        # Clean description
        if 'description' in processed:
            processed['description'] = self.clean_content(processed['description'])
        
        return processed
    
    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """
        Process multiple articles
        
        Args:
            articles: List of article dictionaries
        
        Returns:
            List of processed articles
        """
        return [self.process_article(article) for article in articles]
    
    @staticmethod
    def deduplicate_articles(articles: List[Dict]) -> List[Dict]:
        """
        Remove duplicate articles based on title similarity
        
        Args:
            articles: List of articles
        
        Returns:
            Deduplicated list
        """
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            # Normalize title for comparison
            title = article.get('title', '').lower().strip()
            title_normalized = re.sub(r'[^\w\s]', '', title)
            
            if title_normalized not in seen_titles:
                seen_titles.add(title_normalized)
                unique_articles.append(article)
        
        return unique_articles
    
    @staticmethod
    def filter_by_length(
        articles: List[Dict],
        min_length: int = 100,
        max_length: int = 10000
    ) -> List[Dict]:
        """
        Filter articles by content length
        
        Args:
            articles: List of articles
            min_length: Minimum content length
            max_length: Maximum content length
        
        Returns:
            Filtered articles
        """
        return [
            article for article in articles
            if min_length <= len(article.get('content', '')) <= max_length
        ]
