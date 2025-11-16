"""
Colab Interface - Interacts with Google Colab UI elements
"""
import logging
import time
from typing import Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)


class ColabInterface:
    """Handles interaction with Google Colab UI"""
    
    def __init__(self, driver: webdriver.Chrome, page_load_timeout: int = 60):
        """
        Initialize Colab interface
        
        Args:
            driver: Selenium WebDriver instance
            page_load_timeout: Timeout for page loads
        """
        self.driver = driver
        self.page_load_timeout = page_load_timeout
        self.wait = WebDriverWait(driver, page_load_timeout)
    
    def wait_for_notebook_load(self) -> bool:
        """
        Wait for notebook to fully load
        
        Returns:
            True if notebook loaded successfully
        """
        logger.info("Waiting for notebook to load...")
        
        try:
            # Wait for notebook container to be present
            self.wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    '#main-content, .notebook-container, colab-notebook'
                ))
            )
            
            # Wait a bit for dynamic content to load
            time.sleep(3)
            
            # Check for code cells
            cells = self.driver.find_elements(By.CSS_SELECTOR, '.cell, colab-cell')
            
            if not cells:
                logger.warning("No cells found in notebook")
                return False
            
            logger.info(f"✓ Notebook loaded with {len(cells)} cells")
            return True
            
        except TimeoutException:
            logger.error("Timeout waiting for notebook to load")
            return False
    
    def is_runtime_connected(self) -> bool:
        """
        Check if runtime is connected
        
        Returns:
            True if runtime is connected
        """
        try:
            # Look for runtime status indicators
            # In Colab, a connected runtime shows "RAM" and "Disk" usage
            ram_disk = self.driver.find_elements(
                By.XPATH,
                "//*[contains(text(), 'RAM') or contains(text(), 'Disk')]"
            )
            
            if ram_disk:
                logger.debug("Runtime appears connected (RAM/Disk visible)")
                return True
            
            # Check for "Connect" button - if present, not connected
            connect_buttons = self.driver.find_elements(
                By.XPATH,
                "//button[contains(., 'Connect') or contains(@aria-label, 'Connect')]"
            )
            
            return len(connect_buttons) == 0
            
        except Exception as e:
            logger.debug(f"Runtime connection check error: {e}")
            return False
    
    def connect_runtime(self, timeout: int = 300) -> bool:
        """
        Connect to Colab runtime
        
        Args:
            timeout: Maximum time to wait for connection
            
        Returns:
            True if connected successfully
        """
        if self.is_runtime_connected():
            logger.info("✓ Runtime already connected")
            return True
        
        logger.info("Connecting to runtime...")
        
        try:
            # Find and click Connect button
            connect_button = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(., 'Connect') or contains(@aria-label, 'Connect')]"
                ))
            )
            
            connect_button.click()
            logger.info("Clicked Connect button")
            
            # Wait for runtime to connect
            end_time = time.time() + timeout
            
            while time.time() < end_time:
                if self.is_runtime_connected():
                    logger.info("✓ Runtime connected successfully")
                    time.sleep(2)  # Wait a bit for initialization
                    return True
                
                time.sleep(5)
            
            logger.error("Runtime connection timeout")
            return False
            
        except TimeoutException:
            logger.error("Connect button not found")
            return False
        except Exception as e:
            logger.error(f"Failed to connect runtime: {e}")
            return False
    
    def get_cells(self) -> List:
        """
        Get all notebook cells
        
        Returns:
            List of cell WebElements
        """
        try:
            cells = self.driver.find_elements(By.CSS_SELECTOR, '.cell, colab-cell')
            logger.debug(f"Found {len(cells)} cells")
            return cells
        except Exception as e:
            logger.error(f"Failed to get cells: {e}")
            return []
    
    def get_cell_by_index(self, index: int):
        """
        Get cell by index (0-based)
        
        Args:
            index: Cell index
            
        Returns:
            Cell WebElement or None
        """
        cells = self.get_cells()
        
        if 0 <= index < len(cells):
            return cells[index]
        else:
            logger.error(f"Cell index {index} out of range (total: {len(cells)})")
            return None
    
    def click_cell(self, cell_element) -> bool:
        """
        Click on a cell to select it
        
        Args:
            cell_element: Cell WebElement
            
        Returns:
            True if successful
        """
        try:
            cell_element.click()
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"Failed to click cell: {e}")
            return False
    
    def get_cell_code_element(self, cell_element):
        """
        Get the code editor element within a cell
        
        Args:
            cell_element: Cell WebElement
            
        Returns:
            Code editor element or None
        """
        try:
            # Try different selectors for Colab's code editor
            selectors = [
                '.CodeMirror',
                '.inputarea',
                '.CodeMirror-code',
                'div[role="textbox"]',
                '.monaco-editor'
            ]
            
            for selector in selectors:
                try:
                    code_elem = cell_element.find_element(By.CSS_SELECTOR, selector)
                    if code_elem:
                        return code_elem
                except NoSuchElementException:
                    continue
            
            logger.error("Could not find code editor element")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get code element: {e}")
            return None
    
    def modify_cell_text(self, cell_index: int, new_text: str) -> bool:
        """
        Modify text in a cell
        
        Args:
            cell_index: Index of cell to modify
            new_text: New text content
            
        Returns:
            True if successful
        """
        logger.info(f"Modifying cell {cell_index}...")
        
        try:
            # Get cell
            cell = self.get_cell_by_index(cell_index)
            if not cell:
                return False
            
            # Scroll cell into view
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cell)
            time.sleep(0.5)
            
            # Click cell to focus it
            self.click_cell(cell)
            time.sleep(0.5)
            
            # Try JavaScript method first - more comprehensive selectors
            script = """
            // Find all possible CodeMirror instances in this cell
            var cell = arguments[0];
            var text = arguments[1];
            
            // Method 1: Direct CodeMirror property
            if (cell.CodeMirror) {
                cell.CodeMirror.setValue(text);
                return 'method1';
            }
            
            // Method 2: Find CodeMirror in descendants
            var cmElements = cell.querySelectorAll('.CodeMirror');
            for (var i = 0; i < cmElements.length; i++) {
                if (cmElements[i].CodeMirror) {
                    cmElements[i].CodeMirror.setValue(text);
                    return 'method2';
                }
            }
            
            // Method 3: Monaco editor
            var monacoDiv = cell.querySelector('.monaco-editor');
            if (monacoDiv && window.monaco) {
                var models = window.monaco.editor.getModels();
                if (models.length > 0) {
                    models[0].setValue(text);
                    return 'method3';
                }
            }
            
            // Method 4: Direct textarea manipulation
            var textArea = cell.querySelector('textarea');
            if (textArea) {
                textArea.value = text;
                textArea.dispatchEvent(new Event('input', { bubbles: true }));
                textArea.dispatchEvent(new Event('change', { bubbles: true }));
                return 'method4';
            }
            
            return false;
            """
            
            result = self.driver.execute_script(script, cell, new_text)
            
            if result:
                logger.info(f"✓ Cell {cell_index} modified successfully (JavaScript {result})")
                time.sleep(1)  # Give Colab time to process
                
                # VERIFY the change actually happened
                verify_script = """
                var cell = arguments[0];
                
                // Try to get current content
                if (cell.CodeMirror) {
                    return cell.CodeMirror.getValue();
                }
                
                var cmElements = cell.querySelectorAll('.CodeMirror');
                for (var i = 0; i < cmElements.length; i++) {
                    if (cmElements[i].CodeMirror) {
                        return cmElements[i].CodeMirror.getValue();
                    }
                }
                
                var textArea = cell.querySelector('textarea');
                if (textArea) {
                    return textArea.value;
                }
                
                return null;
                """
                
                current_content = self.driver.execute_script(verify_script, cell)
                
                if current_content and new_text in current_content:
                    logger.info(f"✓ Cell content verified: {len(current_content)} chars")
                    return True
                else:
                    logger.warning(f"Cell content verification failed. Trying keyboard method...")
                    logger.debug(f"Expected text length: {len(new_text)}, Got: {len(current_content) if current_content else 0}")
                    return self._modify_cell_keyboard(cell, new_text)
            
            # If JavaScript failed, try keyboard method
            logger.warning("JavaScript methods failed, trying keyboard input...")
            return self._modify_cell_keyboard(cell, new_text)
            
        except Exception as e:
            logger.error(f"Failed to modify cell {cell_index}: {e}")
            return False
    
    def _modify_cell_keyboard(self, cell_element, new_text: str) -> bool:
        """
        Modify cell using keyboard input (fallback method)
        
        Args:
            cell_element: Cell WebElement
            new_text: New text content
            
        Returns:
            True if successful
        """
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            
            actions = ActionChains(self.driver)
            
            logger.info("Using keyboard method for cell modification...")
            
            # Click cell to focus
            actions.click(cell_element).perform()
            time.sleep(0.5)
            
            # Double-click to enter edit mode
            logger.debug("Entering edit mode (double-click)...")
            actions.double_click(cell_element).perform()
            time.sleep(0.5)
            
            # Select all content (Ctrl+A)
            logger.debug("Selecting all content (Ctrl+A)...")
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time.sleep(0.3)
            
            # Delete selected content
            logger.debug("Deleting content...")
            actions.send_keys(Keys.DELETE).perform()
            time.sleep(0.3)
            
            # Wait a bit to ensure deletion completed
            time.sleep(0.5)
            
            # Use clipboard paste instead of typing line-by-line
            # This is much more reliable and faster for long content
            logger.info(f"Pasting new content ({len(new_text)} chars)...")
            
            try:
                # Copy text to clipboard using JavaScript
                self.driver.execute_script(
                    "navigator.clipboard.writeText(arguments[0]);",
                    new_text
                )
                time.sleep(0.3)
                
                # Paste using Ctrl+V
                logger.debug("Pasting from clipboard (Ctrl+V)...")
                actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                time.sleep(1)  # Give Colab time to process the paste
                
            except Exception as e:
                # Fallback to line-by-line typing if clipboard fails
                logger.warning(f"Clipboard paste failed ({e}), using line-by-line typing...")
                lines = new_text.split('\n')
                for i, line in enumerate(lines):
                    actions.send_keys(line).perform()
                    if i < len(lines) - 1:  # Don't send newline after last line
                        actions.send_keys(Keys.RETURN).perform()
                    time.sleep(0.05)  # Small delay between lines
                    
                    # Log progress for long content
                    if i > 0 and i % 20 == 0:
                        logger.debug(f"Progress: {i}/{len(lines)} lines typed...")
                
                time.sleep(1)  # Give Colab time to process
            
            # Click outside the cell to finalize the edit
            logger.debug("Finalizing edit (ESC)...")
            actions.send_keys(Keys.ESCAPE).perform()
            time.sleep(0.5)
            
            logger.info("✓ Cell modified using keyboard method")
            return True
            
        except Exception as e:
            logger.error(f"Keyboard modification failed: {e}")
            return False
    
    def scroll_to_cell(self, cell_index: int) -> bool:
        """
        Scroll cell into view
        
        Args:
            cell_index: Cell index
            
        Returns:
            True if successful
        """
        try:
            cell = self.get_cell_by_index(cell_index)
            if cell:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    cell
                )
                time.sleep(0.5)
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to scroll to cell: {e}")
            return False
