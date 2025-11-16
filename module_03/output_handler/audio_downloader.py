"""
Audio Downloader - Downloads generated audio files from Colab
"""
import logging
import time
from pathlib import Path
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

logger = logging.getLogger(__name__)


class AudioDownloader:
    """Handles downloading audio files from Google Colab"""
    
    def __init__(self, driver: webdriver.Chrome, download_timeout: int = 120):
        """
        Initialize audio downloader
        
        Args:
            driver: Selenium WebDriver instance
            download_timeout: Timeout for download completion
        """
        self.driver = driver
        self.download_timeout = download_timeout
    
    def trigger_download_via_files_download(self, filepath: str) -> bool:
        """
        Trigger download using google.colab.files.download()
        
        Args:
            filepath: Path to file in Colab filesystem
            
        Returns:
            True if download triggered successfully
        """
        logger.info(f"Triggering download for: {filepath}")
        
        try:
            # JavaScript to execute files.download()
            script = f"""
            // Import files module
            var colab = google.colab || {{}};
            colab.files = colab.files || {{}};
            
            // Trigger download
            if (colab.files.download) {{
                colab.files.download('{filepath}');
                return true;
            }}
            return false;
            """
            
            success = self.driver.execute_script(script)
            
            if success:
                logger.info("✓ Download triggered via files.download()")
                return True
            else:
                logger.warning("files.download() not available")
                return False
                
        except Exception as e:
            logger.error(f"Failed to trigger download: {e}")
            return False
    
    def trigger_download_via_cell_execution(self, cell_index: int) -> bool:
        """
        Trigger download by executing a cell that contains files.download()
        
        Args:
            cell_index: Index of cell to execute
            
        Returns:
            True if successful
        """
        logger.info(f"Executing download cell {cell_index}...")
        
        try:
            cells = self.driver.find_elements(By.CSS_SELECTOR, '.cell, colab-cell')
            
            if cell_index >= len(cells):
                logger.error(f"Cell index {cell_index} out of range")
                return False
            
            cell = cells[cell_index]
            
            # Click and execute cell
            cell.click()
            time.sleep(0.5)
            
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
            
            logger.info("✓ Download cell executed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to execute download cell: {e}")
            return False
    
    def wait_for_download_complete(self, download_dir: Path, expected_filename: str) -> Optional[Path]:
        """
        Wait for download to complete
        
        Args:
            download_dir: Directory where file will be downloaded
            expected_filename: Expected filename (e.g., "output_vietnamese.wav")
            
        Returns:
            Path to downloaded file if successful, None otherwise
        """
        logger.info(f"Waiting for download: {expected_filename}")
        
        download_path = download_dir / expected_filename
        end_time = time.time() + self.download_timeout
        
        while time.time() < end_time:
            # Check if file exists and is not a partial download
            if download_path.exists():
                # Check it's not a .crdownload file
                crdownload = download_dir / f"{expected_filename}.crdownload"
                if not crdownload.exists():
                    # Verify file size > 0
                    if download_path.stat().st_size > 0:
                        logger.info(f"✓ Download complete: {download_path}")
                        return download_path
            
            # Check for .crdownload files (in-progress)
            crdownload_files = list(download_dir.glob("*.crdownload"))
            if crdownload_files:
                logger.debug(f"Download in progress... ({len(crdownload_files)} partial files)")
            
            time.sleep(2)
        
        logger.error(f"Download timeout ({self.download_timeout}s)")
        return None
    
    def find_and_trigger_download(self, colab_filepath: str) -> bool:
        """
        Find audio file in Colab file browser and trigger download
        
        Args:
            colab_filepath: Path to file in Colab (e.g., "/content/output_vietnamese.wav")
            
        Returns:
            True if download triggered
        """
        logger.info(f"Looking for file in Colab: {colab_filepath}")
        
        try:
            # Try to use files.download() first
            if self.trigger_download_via_files_download(colab_filepath):
                return True
            
            # Fallback: try to find file in file browser
            logger.info("Trying file browser method...")
            
            # Open file browser (left sidebar)
            file_browser_button = self.driver.find_elements(
                By.CSS_SELECTOR,
                '[aria-label*="Files"], [title*="Files"]'
            )
            
            if file_browser_button:
                file_browser_button[0].click()
                time.sleep(2)
                
                # Look for the file
                filename = Path(colab_filepath).name
                file_elements = self.driver.find_elements(
                    By.XPATH,
                    f"//*[contains(text(), '{filename}')]"
                )
                
                if file_elements:
                    # Right-click on file
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(self.driver)
                    actions.context_click(file_elements[0]).perform()
                    time.sleep(1)
                    
                    # Click Download option
                    download_option = self.driver.find_elements(
                        By.XPATH,
                        "//*[contains(text(), 'Download')]"
                    )
                    
                    if download_option:
                        download_option[0].click()
                        logger.info("✓ Download triggered via file browser")
                        return True
            
            logger.warning("Could not trigger download via file browser")
            return False
            
        except Exception as e:
            logger.error(f"Failed to find and trigger download: {e}")
            return False
    
    def verify_audio_file(self, filepath: Path) -> bool:
        """
        Verify downloaded audio file is valid
        
        Args:
            filepath: Path to audio file
            
        Returns:
            True if file is valid
        """
        if not filepath.exists():
            logger.error(f"File does not exist: {filepath}")
            return False
        
        file_size = filepath.stat().st_size
        
        if file_size == 0:
            logger.error("File is empty")
            return False
        
        # Check file extension
        if not filepath.suffix.lower() in ['.wav', '.mp3', '.ogg']:
            logger.warning(f"Unexpected file extension: {filepath.suffix}")
        
        # Basic size check (TTS audio should be at least a few KB)
        if file_size < 1000:
            logger.warning(f"File seems too small: {file_size} bytes")
            return False
        
        logger.info(f"✓ Audio file verified: {file_size} bytes")
        return True
