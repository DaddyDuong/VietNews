"""
Logger configuration for module_03
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(
    name: str = "module_03",
    log_file: Path = None,
    log_level: str = "INFO",
    log_format: str = None,
    console: bool = True
) -> logging.Logger:
    """
    Setup logger with file and console handlers
    
    Args:
        name: Logger name
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log message format
        console: Whether to log to console
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Default format
    if not log_format:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(exist_ok=True, parents=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def log_section(logger: logging.Logger, title: str, width: int = 70):
    """
    Log a section header
    
    Args:
        logger: Logger instance
        title: Section title
        width: Width of separator line
    """
    logger.info("=" * width)
    logger.info(title.center(width))
    logger.info("=" * width)


def log_step(logger: logging.Logger, step_num: int, total_steps: int, description: str):
    """
    Log a step in a process
    
    Args:
        logger: Logger instance
        step_num: Current step number
        total_steps: Total number of steps
        description: Step description
    """
    logger.info(f"[{step_num}/{total_steps}] {description}")


def log_error_with_traceback(logger: logging.Logger, error: Exception):
    """
    Log error with traceback
    
    Args:
        logger: Logger instance
        error: Exception to log
    """
    import traceback
    logger.error(f"Error: {error}")
    logger.debug(traceback.format_exc())
