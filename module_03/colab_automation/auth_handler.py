"""
Authentication Handler - Manages Google Colab authentication
"""
import json
import logging
import time
from pathlib import Path
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class AuthHandler:
    """Handles Google Colab authentication"""
    
    def __init__(
        self,
        driver: webdriver.Chrome,
        cookies_file: Optional[Path] = None,
        auth_method: str = "manual"
    ):
        """
        Initialize auth handler
        
        Args:
            driver: Selenium WebDriver instance
            cookies_file: Path to cookies JSON file
            auth_method: "manual" or "cookies"
        """
        self.driver = driver
        self.cookies_file = cookies_file
        self.auth_method = auth_method
    
    def save_cookies(self):
        """Save current cookies to file"""
        if not self.cookies_file:
            logger.warning("No cookies file specified, skipping save")
            return
        
        try:
            cookies = self.driver.get_cookies()
            
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            
            logger.info(f"Cookies saved to: {self.cookies_file}")
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
    
    def load_cookies(self) -> bool:
        """
        Load cookies from file
        
        Returns:
            True if cookies loaded successfully
        """
        if not self.cookies_file or not self.cookies_file.exists():
            logger.warning(f"Cookies file not found: {self.cookies_file}")
            return False
        
        try:
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    logger.debug(f"Skipping cookie: {e}")
            
            logger.info(f"Cookies loaded from: {self.cookies_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to load cookies: {e}")
            return False
    
    def wait_for_manual_auth(self, timeout: int = 300) -> bool:
        """
        Wait for user to manually authenticate
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if authenticated
        """
        logger.info("=" * 70)
        logger.info("MANUAL AUTHENTICATION REQUIRED")
        logger.info("=" * 70)
        logger.info("Please log in to Google Colab in the browser window")
        logger.info(f"Waiting up to {timeout} seconds...")
        logger.info("=" * 70)
        
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            if self.is_authenticated():
                logger.info("✓ Authentication successful!")
                self.save_cookies()
                return True
            
            time.sleep(5)
        
        logger.error("Authentication timeout")
        return False
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated to Google Colab
        
        Returns:
            True if authenticated
        """
        try:
            # Check for Colab-specific elements that indicate logged in state
            # This is a heuristic approach
            
            # Check for user profile icon or menu
            user_elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[aria-label*="Account"], [aria-label*="Google Account"], .gb_d'
            )
            
            if user_elements:
                logger.debug("User account elements found")
                return True
            
            # Check for sign-in button (if present, not authenticated)
            signin_buttons = self.driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'Sign in')]"
            )
            
            if signin_buttons:
                logger.debug("Sign in button found - not authenticated")
                return False
            
            # If we can access the notebook toolbar, likely authenticated
            toolbar = self.driver.find_elements(
                By.CSS_SELECTOR,
                '.notebook-toolbar, colab-toolbar'
            )
            
            return len(toolbar) > 0
            
        except Exception as e:
            logger.debug(f"Authentication check error: {e}")
            return False
    
    def authenticate(self, colab_url: str = None) -> bool:
        """
        Perform authentication based on configured method
        
        Args:
            colab_url: Colab notebook URL to navigate to after auth
        
        Returns:
            True if authentication successful
        """
        logger.info(f"Authenticating using method: {self.auth_method}")
        
        if self.auth_method == "cookies":
            # Navigate to Google domain first to set cookies
            logger.debug("Navigating to google.com to load cookies...")
            self.driver.get("https://accounts.google.com")
            time.sleep(2)
            
            # Try loading cookies
            if self.load_cookies():
                # Navigate back to Colab if URL provided
                if colab_url:
                    logger.debug(f"Navigating to Colab with cookies...")
                    self.driver.get(colab_url)
                    time.sleep(5)
                else:
                    # Refresh to apply cookies
                    self.driver.refresh()
                    time.sleep(3)
                
                if self.is_authenticated():
                    logger.info("✓ Authenticated using saved cookies")
                    return True
                else:
                    logger.warning("Cookies loaded but authentication failed")
                    logger.info("Falling back to manual authentication...")
        
        # Fall back to manual authentication
        return self.wait_for_manual_auth()
    
    def verify_notebook_access(self) -> bool:
        """
        Verify that we can access and edit the notebook
        
        Returns:
            True if notebook is accessible
        """
        try:
            # Check for notebook cells
            cells = self.driver.find_elements(
                By.CSS_SELECTOR,
                '.cell, colab-cell, .code-cell'
            )
            
            if not cells:
                logger.error("No notebook cells found")
                return False
            
            logger.info(f"✓ Found {len(cells)} cells in notebook")
            return True
            
        except Exception as e:
            logger.error(f"Failed to verify notebook access: {e}")
            return False
