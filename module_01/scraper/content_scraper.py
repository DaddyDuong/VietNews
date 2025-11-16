"""
Content scraper for news articles
"""
import requests
import time
from typing import Optional
from bs4 import BeautifulSoup
from config import (
    REQUEST_TIMEOUT, 
    RETRY_ATTEMPTS, 
    USER_AGENT, 
    DELAY_BETWEEN_REQUESTS,
    VNEXPRESS_SELECTORS
)
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ContentScraper:
    """Scrapes full article content from news URLs"""
    
    def __init__(self):
        self.timeout = REQUEST_TIMEOUT
        self.retry_attempts = RETRY_ATTEMPTS
        self.delay = DELAY_BETWEEN_REQUESTS
        self.headers = {
            'User-Agent': USER_AGENT
        }
    
    def extract_content(self, url: str, html: str) -> Optional[str]:
        """
        Extract content based on the source website
        
        Args:
            url: Article URL
            html: HTML content
        
        Returns:
            Extracted content or None
        """
        if 'vnexpress.net' in url:
            return self.extract_vnexpress_content(html)
        elif 'tuoitre.vn' in url or 'thanhnien.vn' in url:
            return self.extract_tuoitre_content(html)
        elif 'dantri.com.vn' in url:
            return self.extract_dantri_content(html)
        elif 'vtv.vn' in url:
            return self.extract_vtv_content(html)
        elif 'vietnamnet.vn' in url:
            return self.extract_vietnamnet_content(html)
        else:
            # Try generic extraction
            logger.warning(f"Unknown source, trying generic extraction for: {url}")
            return self.extract_vnexpress_content(html)
    
    def scrape(self, url: str) -> Optional[str]:
        """
        Scrape article content from URL
        
        Args:
            url: Article URL
        
        Returns:
            HTML content as string, or None if failed
        """
        logger.info(f"Scraping article: {url}")
        
        # Rate limiting
        time.sleep(self.delay)
        
        for attempt in range(1, self.retry_attempts + 1):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # Ensure proper encoding
                response.encoding = response.apparent_encoding
                
                logger.info(f"Successfully scraped: {url}")
                return response.text
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt}/{self.retry_attempts} failed for {url}: {e}")
                
                if attempt == self.retry_attempts:
                    logger.error(f"Failed to scrape after {self.retry_attempts} attempts: {url}")
                    return None
                
                # Wait before retry
                time.sleep(self.delay)
        
        return None
    
    def extract_vnexpress_content(self, html: str) -> Optional[str]:
        """
        Extract article content from VnExpress HTML
        
        Args:
            html: HTML content
        
        Returns:
            Extracted content or None
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check if this is a video article (skip video articles)
            if self._is_video_article(soup):
                logger.info("Skipping video article")
                return "VIDEO_ARTICLE"  # Special marker for video articles
            
            # Try to find article body - support both <article> and <div>
            article_body = soup.select_one('article.fck_detail')
            if not article_body:
                article_body = soup.select_one('div.fck_detail')
            
            if not article_body:
                logger.warning("Could not find article body")
                return None
            
            # Extract paragraphs with class 'Normal'
            paragraphs = article_body.select('p.Normal')
            
            if not paragraphs:
                # Fallback: get all <p> tags without specific exclusions
                all_paragraphs = article_body.find_all('p')
                paragraphs = [p for p in all_paragraphs if self._is_valid_paragraph(p)]
                logger.debug(f"Using fallback: found {len(paragraphs)} paragraphs")
            
            # Combine paragraphs
            content_parts = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 10:  # Skip very short paragraphs
                    content_parts.append(text)
            
            content = '\n\n'.join(content_parts)
            
            if not content:
                logger.warning("No content extracted")
                return None
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting VnExpress content: {e}")
            return None
    
    def extract_tuoitre_content(self, html: str) -> Optional[str]:
        """
        Extract article content from Tuoi Tre HTML
        
        Args:
            html: HTML content
        
        Returns:
            Extracted content or None
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check if this is a video article
            if self._is_video_article(soup):
                logger.info("Skipping video article")
                return "VIDEO_ARTICLE"
            
            # Find content container
            content_div = soup.select_one('div.detail-content')
            if not content_div:
                logger.warning("Could not find article body")
                return None
            
            # Extract all paragraphs
            paragraphs = content_div.find_all('p')
            
            if not paragraphs:
                logger.warning("No paragraphs found")
                return None
            
            # Combine paragraphs
            content_parts = []
            for p in paragraphs:
                # Skip paragraphs from related articles section
                # Check if any ancestor has VCSortableInPreviewMode class
                is_related_article = False
                for ancestor in p.parents:
                    ancestor_classes = ancestor.get('class', [])
                    if 'VCSortableInPreviewMode' in ancestor_classes:
                        is_related_article = True
                        break
                
                if is_related_article:
                    continue
                
                # Skip paragraphs that are likely metadata
                if self._is_valid_paragraph(p):
                    text = p.get_text(strip=True)
                    if text and len(text) > 10:
                        content_parts.append(text)
            
            content = '\n\n'.join(content_parts)
            
            if not content:
                logger.warning("No content extracted")
                return None
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting Tuoi Tre content: {e}")
            return None
    
    def extract_dantri_content(self, html: str) -> Optional[str]:
        """
        Extract article content from Dan Tri HTML
        
        Args:
            html: HTML content
        
        Returns:
            Extracted content or None
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check if this is a video article
            if self._is_video_article(soup):
                logger.info("Skipping video article")
                return "VIDEO_ARTICLE"
            
            # Find content container - support both regular and e-magazine formats
            content_div = soup.select_one('div.singular-content')
            if not content_div:
                # Try e-magazine format (DNews)
                content_div = soup.select_one('div.e-magazine__body')
            
            if not content_div:
                logger.warning("Could not find article body (tried singular-content and e-magazine__body)")
                return None
            
            # Extract all paragraphs
            paragraphs = content_div.find_all('p')
            
            if not paragraphs:
                logger.warning("No paragraphs found")
                return None
            
            # Combine paragraphs
            content_parts = []
            for p in paragraphs:
                # Skip paragraphs from related articles section
                # Check if any ancestor has VCSortableInPreviewMode class
                is_related_article = False
                for ancestor in p.parents:
                    ancestor_classes = ancestor.get('class', [])
                    if 'VCSortableInPreviewMode' in ancestor_classes:
                        is_related_article = True
                        break
                
                if is_related_article:
                    continue
                
                # Skip paragraphs that are likely metadata
                if self._is_valid_paragraph(p):
                    text = p.get_text(strip=True)
                    if text and len(text) > 10:
                        content_parts.append(text)
            
            content = '\n\n'.join(content_parts)
            
            if not content:
                logger.warning("No content extracted")
                return None
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting Dan Tri content: {e}")
            return None
    
    def _is_video_article(self, soup: BeautifulSoup) -> bool:
        """
        Check if the article is a video article
        
        Args:
            soup: BeautifulSoup object
        
        Returns:
            True if it's a video article
        """
        # Check for video indicators
        video_indicators = [
            soup.select_one('div.box_video_title'),
            soup.select_one('div.video_player_detail'),
            soup.find('meta', {'property': 'og:type', 'content': 'video'}),
        ]
        
        # Check if any video indicator is present
        if any(video_indicators):
            return True
        
        # Check if the main content is just a video link
        article_body = soup.select_one('article.fck_detail') or soup.select_one('div.fck_detail')
        if article_body:
            text_content = article_body.get_text(strip=True)
            # If content contains "Video:" and is very short, it's likely a video article
            if 'Video:' in text_content and len(text_content) < 150:
                return True
            
            # Check if there are very few paragraphs (likely just video caption)
            paragraphs = article_body.find_all('p')
            valid_paragraphs = [p for p in paragraphs if len(p.get_text(strip=True)) > 20]
            if len(valid_paragraphs) <= 1:
                return True
        
        return False
    
    def _is_valid_paragraph(self, p) -> bool:
        """
        Check if a paragraph should be included in content
        
        Args:
            p: BeautifulSoup paragraph element
        
        Returns:
            True if paragraph is valid content
        """
        # Skip paragraphs with certain classes that indicate non-content
        exclude_classes = ['description', 'author', 'date', 'caption', 'Image']
        p_classes = p.get('class', [])
        
        if any(cls in p_classes for cls in exclude_classes):
            return False
        
        # Skip empty paragraphs
        text = p.get_text(strip=True)
        if not text or len(text) < 10:
            return False
        
        return True
    
    def extract_vietnamnet_content(self, html: str) -> Optional[str]:
        """
        Extract article content from VietnamNet HTML
        
        Args:
            html: HTML content
        
        Returns:
            Extracted content or None
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check if this is a video article
            if self._is_video_article(soup):
                logger.info("Skipping video article")
                return "VIDEO_ARTICLE"
            
            # Find content container
            content_div = soup.select_one('div.maincontent')
            if not content_div:
                content_div = soup.select_one('div.main-content')
            
            if not content_div:
                logger.warning("Could not find article body")
                return None
            
            # Extract all paragraphs
            paragraphs = content_div.find_all('p')
            
            if not paragraphs:
                logger.warning("No paragraphs found")
                return None
            
            # Combine paragraphs
            content_parts = []
            for p in paragraphs:
                # Skip paragraphs from related articles or ads
                # Check if any ancestor has certain classes
                is_excluded = False
                for ancestor in p.parents:
                    ancestor_classes = ancestor.get('class', [])
                    # Skip content in sidebars, related articles, ads
                    exclude_ancestor_classes = ['summary__content', 'sidebar', 'related', 'advertise', 'ads']
                    if any(cls in ancestor_classes for cls in exclude_ancestor_classes):
                        is_excluded = True
                        break
                
                if is_excluded:
                    continue
                
                # Skip paragraphs that are likely metadata
                if self._is_valid_paragraph(p):
                    text = p.get_text(strip=True)
                    if text and len(text) > 10:
                        content_parts.append(text)
            
            content = '\n\n'.join(content_parts)
            
            if not content:
                logger.warning("No content extracted")
                return None
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting VietnamNet content: {e}")
            return None
    
    def extract_vtv_content(self, html: str) -> Optional[str]:
        """
        Extract article content from VTV
        
        Args:
            html: HTML content
        
        Returns:
            Extracted content text or None
        """
        try:
            soup = BeautifulSoup(html, 'html5lib')
            
            # Check if it's a video article
            if self._is_video_article(soup):
                logger.info("Video article detected, skipping content extraction")
                return "VIDEO_ARTICLE"
            
            # Find main content container
            content_div = soup.find('div', class_='detail-content')
            
            if not content_div:
                logger.warning("Could not find content container (div.detail-content)")
                return None
            
            # Extract all paragraphs
            paragraphs = []
            for p in content_div.find_all('p'):
                # Skip if paragraph is inside excluded elements
                if p.find_parent(['aside', 'figure']):
                    continue
                
                # Validate and clean paragraph
                if self._is_valid_paragraph(p):
                    text = p.get_text(strip=True)
                    paragraphs.append(text)
            
            content = '\n\n'.join(paragraphs)
            
            if not content:
                logger.warning("No content extracted")
                return None
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting VTV content: {e}")
            return None
