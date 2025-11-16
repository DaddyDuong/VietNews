"""
Browser Driver - Setup and manage browser instance for Colab automation
"""
import os
import logging
import time
from pathlib import Path
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class BrowserDriver:
    """Manages browser instance for Colab automation"""
    
    def __init__(
        self,
        headless: bool = False,
        download_dir: Optional[str] = None,
        window_width: int = 1920,
        window_height: int = 1080
    ):
        """
        Initialize browser driver
        
        Args:
            headless: Run browser in headless mode
            download_dir: Directory for downloads
            window_width: Browser window width
            window_height: Browser window height
        """
        self.headless = headless
        self.download_dir = download_dir or os.getcwd()
        self.window_width = window_width
        self.window_height = window_height
        self.driver: Optional[webdriver.Chrome] = None
    
    def setup_chrome_options(self) -> Options:
        """
        Setup Chrome options for Colab automation
        
        Returns:
            Configured Chrome options
        """
        options = Options()
        
        # Headless mode
        if self.headless:
            options.add_argument('--headless=new')
            logger.info("Running in headless mode")
        
        # Window size
        options.add_argument(f'--window-size={self.window_width},{self.window_height}')
        
        # Download preferences
        prefs = {
            'download.default_directory': str(Path(self.download_dir).absolute()),
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': False,
            'profile.default_content_settings.popups': 0,
        }
        options.add_experimental_option('prefs', prefs)
        
        # Additional options for stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        # User agent
        options.add_argument(
            '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        return options
    
    def start(self) -> webdriver.Chrome:
        """
        Start browser instance
        
        Returns:
            WebDriver instance
        """
        logger.info("Starting Chrome browser...")
        
        try:
            options = self.setup_chrome_options()
            
            # Use webdriver-manager to handle chromedriver automatically
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Set timeouts
            self.driver.implicitly_wait(10)
            
            logger.info(f"Browser started successfully (headless={self.headless})")
            logger.info(f"Download directory: {self.download_dir}")
            
            return self.driver
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise
    
    def navigate(self, url: str, wait: int = 3):
        """
        Navigate to a URL
        
        Args:
            url: URL to navigate to
            wait: Seconds to wait after navigation
        """
        if not self.driver:
            raise RuntimeError("Browser not started. Call start() first.")
        
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)
        time.sleep(wait)
    
    def refresh(self, wait: int = 3):
        """
        Refresh current page
        
        Args:
            wait: Seconds to wait after refresh
        """
        if not self.driver:
            raise RuntimeError("Browser not started")
        
        logger.info("Refreshing page...")
        self.driver.refresh()
        time.sleep(wait)
    
    def screenshot(self, filepath: str) -> bool:
        """
        Take screenshot
        
        Args:
            filepath: Path to save screenshot
            
        Returns:
            True if successful
        """
        if not self.driver:
            return False
        
        try:
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return False
    
    def execute_script(self, script: str):
        """
        Execute JavaScript in browser
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            Result of script execution
        """
        if not self.driver:
            raise RuntimeError("Browser not started")
        
        return self.driver.execute_script(script)
    
    def wait_for_downloads(self, timeout: int = 60) -> bool:
        """
        Wait for all downloads to complete
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if downloads completed, False if timeout
        """
        logger.info("Waiting for downloads to complete...")
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            # Check for .crdownload files (Chrome partial downloads)
            download_path = Path(self.download_dir)
            partial_files = list(download_path.glob("*.crdownload"))
            
            if not partial_files:
                logger.info("All downloads completed")
                return True
            
            time.sleep(1)
        
        logger.warning("Download timeout reached")
        return False
    
    def close(self):
        """Close browser instance"""
        if self.driver:
            logger.info("Closing browser...")
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
            finally:
                self.driver = None
    
    def __enter__(self):
        """Context manager entry"""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
        return False
