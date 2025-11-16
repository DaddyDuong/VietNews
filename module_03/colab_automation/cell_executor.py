"""
Cell Executor - Executes notebook cells and monitors status
"""
import logging
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class CellExecutor:
    """Executes notebook cells and monitors execution status"""
    
    def __init__(
        self,
        driver: webdriver.Chrome,
        cell_timeout: int = 300,
        check_interval: int = 2
    ):
        """
        Initialize cell executor
        
        Args:
            driver: Selenium WebDriver instance
            cell_timeout: Timeout for cell execution (seconds)
            check_interval: Interval to check cell status (seconds)
        """
        self.driver = driver
        self.cell_timeout = cell_timeout
        self.check_interval = check_interval
    
    def run_all_cells(self, timeout: int = 600) -> bool:
        """
        Execute all cells using Colab's "Run all" command
        
        Args:
            timeout: Maximum time to wait for all cells to complete
            
        Returns:
            True if all cells executed successfully
        """
        logger.info("Executing all cells via 'Run all'...")
        
        try:
            # Use Ctrl+F9 keyboard shortcut for "Run all"
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            
            # Ctrl+F9 = Run all cells
            actions.key_down(Keys.CONTROL).send_keys(Keys.F9).key_up(Keys.CONTROL).perform()
            time.sleep(2)
            
            logger.info("✓ 'Run all' command triggered")
            logger.info(f"Waiting up to {timeout}s for all cells to complete...")
            
            # Wait for all cells to finish
            return self.wait_for_all_cells_complete(timeout)
            
        except Exception as e:
            logger.error(f"Failed to run all cells: {e}")
            return False
    
    def wait_for_all_cells_complete(self, timeout: int) -> bool:
        """
        Wait for all cells to complete execution
        
        Args:
            timeout: Maximum time to wait
            
        Returns:
            True if all cells completed
        """
        start_time = time.time()
        end_time = start_time + timeout
        
        last_status = None
        
        while time.time() < end_time:
            # Check if any cells are still running
            running_cells = self.driver.find_elements(
                By.CSS_SELECTOR,
                '.cell.executing, .cell.running, [class*="executing"], [class*="running"]'
            )
            
            if not running_cells:
                # Check if there are any errors
                error_cells = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    '.cell .error, .cell .err'
                )
                
                if error_cells:
                    logger.warning(f"Found {len(error_cells)} cells with errors")
                
                elapsed = time.time() - start_time
                logger.info(f"✓ All cells completed in {elapsed:.1f}s")
                return True
            
            # Log progress
            current_status = f"{len(running_cells)} cells still running"
            if current_status != last_status:
                logger.info(current_status)
                last_status = current_status
            
            time.sleep(self.check_interval)
        
        logger.error(f"Timeout waiting for cells to complete ({timeout}s)")
        return False
    
    def execute_cell(self, cell_element, timeout: Optional[int] = None) -> bool:
        """
        Execute a single cell
        
        Args:
            cell_element: Cell WebElement to execute
            timeout: Override default timeout
            
        Returns:
            True if execution successful
        """
        timeout = timeout or self.cell_timeout
        
        try:
            # Click cell to select it
            cell_element.click()
            time.sleep(0.5)
            
            # Execute using Shift+Enter
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
            
            logger.debug("Cell execution triggered")
            
            # Wait for execution to complete
            return self.wait_for_cell_completion(cell_element, timeout)
            
        except Exception as e:
            logger.error(f"Failed to execute cell: {e}")
            return False
    
    def execute_cell_by_index(self, cell_index: int, timeout: Optional[int] = None) -> bool:
        """
        Execute cell by index
        
        Args:
            cell_index: Index of cell to execute (0-based)
            timeout: Override default timeout
            
        Returns:
            True if execution successful
        """
        logger.info(f"Executing cell {cell_index}...")
        
        try:
            # Get all cells
            cells = self.driver.find_elements(By.CSS_SELECTOR, '.cell, colab-cell')
            
            if cell_index >= len(cells):
                logger.error(f"Cell index {cell_index} out of range (total: {len(cells)})")
                return False
            
            cell = cells[cell_index]
            
            # Scroll to cell
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                cell
            )
            time.sleep(0.5)
            
            # Execute cell
            success = self.execute_cell(cell, timeout)
            
            if success:
                logger.info(f"✓ Cell {cell_index} executed successfully")
            else:
                logger.error(f"✗ Cell {cell_index} execution failed or timed out")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to execute cell {cell_index}: {e}")
            return False
    
    def wait_for_cell_completion(self, cell_element, timeout: int) -> bool:
        """
        Wait for cell to complete execution
        
        Args:
            cell_element: Cell WebElement
            timeout: Maximum time to wait
            
        Returns:
            True if cell completed successfully
        """
        start_time = time.time()
        end_time = start_time + timeout
        
        while time.time() < end_time:
            status = self.get_cell_status(cell_element)
            
            if status == "completed":
                elapsed = time.time() - start_time
                logger.debug(f"Cell completed in {elapsed:.1f}s")
                return True
            elif status == "error":
                logger.error("Cell execution resulted in error")
                return False
            elif status == "running":
                logger.debug("Cell still running...")
            
            time.sleep(self.check_interval)
        
        logger.error(f"Cell execution timeout ({timeout}s)")
        return False
    
    def get_cell_status(self, cell_element) -> str:
        """
        Get execution status of a cell
        
        Args:
            cell_element: Cell WebElement
            
        Returns:
            Status: "running", "completed", "error", "idle"
        """
        try:
            # Check for execution indicator (spinning icon or progress)
            running_indicators = cell_element.find_elements(
                By.CSS_SELECTOR,
                '.spinner, .running, [class*="executing"], [class*="running"]'
            )
            
            if running_indicators:
                return "running"
            
            # Check for checkmark (completed)
            completed_indicators = cell_element.find_elements(
                By.CSS_SELECTOR,
                '.completed, [class*="completed"], [class*="done"]'
            )
            
            # Also check for execution count which indicates completion
            execution_count = cell_element.find_elements(
                By.CSS_SELECTOR,
                '.execution_count, [class*="execution"], [class*="count"]'
            )
            
            if completed_indicators or execution_count:
                # Check if there's an error
                errors = cell_element.find_elements(
                    By.CSS_SELECTOR,
                    '.error, .err, [class*="error"]'
                )
                
                if errors:
                    return "error"
                
                return "completed"
            
            # Check execution counter in the output
            # Colab shows [*] while running, [number] when done
            try:
                # Look for execution counter text
                counter_text = cell_element.text
                if '[*]' in counter_text or '[ ]' in counter_text:
                    return "running"
                elif counter_text and '[' in counter_text and ']' in counter_text:
                    return "completed"
            except:
                pass
            
            return "idle"
            
        except Exception as e:
            logger.debug(f"Status check error: {e}")
            return "idle"
    
    def execute_cells_sequence(self, cell_indices: list, individual_timeout: Optional[int] = None) -> dict:
        """
        Execute multiple cells in sequence
        
        Args:
            cell_indices: List of cell indices to execute
            individual_timeout: Timeout for each individual cell
            
        Returns:
            Dict with execution results
        """
        results = {
            'total': len(cell_indices),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        logger.info(f"Executing {len(cell_indices)} cells in sequence...")
        
        for i, cell_index in enumerate(cell_indices, 1):
            logger.info(f"[{i}/{len(cell_indices)}] Executing cell {cell_index}...")
            
            success = self.execute_cell_by_index(cell_index, individual_timeout)
            
            results['details'].append({
                'cell_index': cell_index,
                'success': success
            })
            
            if success:
                results['successful'] += 1
            else:
                results['failed'] += 1
                logger.warning(f"Cell {cell_index} failed, continuing anyway...")
            
            # Small delay between cells
            time.sleep(1)
        
        logger.info(
            f"Sequence complete: {results['successful']}/{results['total']} successful"
        )
        
        return results
    
    def get_cell_output(self, cell_element) -> Optional[str]:
        """
        Get output text from a cell
        
        Args:
            cell_element: Cell WebElement
            
        Returns:
            Output text or None
        """
        try:
            output_elements = cell_element.find_elements(
                By.CSS_SELECTOR,
                '.output, .output_area, [class*="output"]'
            )
            
            if output_elements:
                return output_elements[0].text
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to get cell output: {e}")
            return None
    
    def check_for_errors(self, cell_element) -> Optional[str]:
        """
        Check if cell has error output
        
        Args:
            cell_element: Cell WebElement
            
        Returns:
            Error text if error found, None otherwise
        """
        try:
            error_elements = cell_element.find_elements(
                By.CSS_SELECTOR,
                '.error, .err, [class*="error"], .traceback'
            )
            
            if error_elements:
                return error_elements[0].text
            
            return None
            
        except Exception as e:
            logger.debug(f"Error check failed: {e}")
            return None
