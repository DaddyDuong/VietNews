"""
Retry handler for failed operations
"""
import logging
import time
from typing import Callable, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_failure(
    max_retries: int = 3,
    delay: float = 5.0,
    backoff: float = 1.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry function on failure
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries:
                        logger.error(f"{func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                    )
                    logger.info(f"Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return None
        
        return wrapper
    return decorator


class RetryHandler:
    """Handler for retrying operations with custom logic"""
    
    def __init__(
        self,
        max_retries: int = 3,
        delay: float = 5.0,
        backoff: float = 1.0
    ):
        """
        Initialize retry handler
        
        Args:
            max_retries: Maximum number of retry attempts
            delay: Initial delay between retries (seconds)
            backoff: Multiplier for delay after each retry
        """
        self.max_retries = max_retries
        self.delay = delay
        self.backoff = backoff
    
    def execute(
        self,
        func: Callable,
        *args,
        exception_types: tuple = (Exception,),
        on_retry: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            exception_types: Tuple of exceptions to catch and retry
            on_retry: Optional callback to execute before retry
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries fail
        """
        current_delay = self.delay
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                
                if attempt > 0:
                    logger.info(f"✓ {func.__name__} succeeded on attempt {attempt + 1}")
                
                return result
                
            except exception_types as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    logger.error(
                        f"{func.__name__} failed after {self.max_retries} retries: {e}"
                    )
                    raise
                
                logger.warning(
                    f"{func.__name__} failed (attempt {attempt + 1}/{self.max_retries + 1}): {e}"
                )
                
                # Execute retry callback if provided
                if on_retry:
                    try:
                        on_retry(attempt, e)
                    except Exception as callback_error:
                        logger.warning(f"Retry callback failed: {callback_error}")
                
                logger.info(f"Retrying in {current_delay}s...")
                time.sleep(current_delay)
                current_delay *= backoff
        
        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
    
    def execute_with_condition(
        self,
        func: Callable,
        condition: Callable[[Any], bool],
        *args,
        **kwargs
    ) -> Any:
        """
        Execute function and retry if result doesn't meet condition
        
        Args:
            func: Function to execute
            condition: Condition to check result (returns True if acceptable)
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
            
        Raises:
            RuntimeError: If all retries fail to meet condition
        """
        current_delay = self.delay
        
        for attempt in range(self.max_retries + 1):
            result = func(*args, **kwargs)
            
            if condition(result):
                if attempt > 0:
                    logger.info(f"✓ {func.__name__} met condition on attempt {attempt + 1}")
                return result
            
            if attempt == self.max_retries:
                logger.error(
                    f"{func.__name__} failed to meet condition after {self.max_retries} retries"
                )
                raise RuntimeError(f"Result did not meet condition after {self.max_retries} retries")
            
            logger.warning(
                f"{func.__name__} result did not meet condition (attempt {attempt + 1}/{self.max_retries + 1})"
            )
            logger.info(f"Retrying in {current_delay}s...")
            time.sleep(current_delay)
            current_delay *= self.backoff
        
        return result
