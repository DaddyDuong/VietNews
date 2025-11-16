"""
Bulletin Reader - Reads bulletin text files from module_02 output
"""
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class BulletinReader:
    """Read bulletin text files from module_02 output directory"""
    
    def __init__(self, module_02_output_dir: Path):
        """
        Initialize bulletin reader
        
        Args:
            module_02_output_dir: Path to module_02/output directory
        """
        self.output_dir = Path(module_02_output_dir)
        
        if not self.output_dir.exists():
            raise FileNotFoundError(
                f"Module 02 output directory not found: {self.output_dir}"
            )
    
    def get_bulletin_path(self, date: datetime) -> Path:
        """
        Get path to bulletin file for a specific date
        
        Args:
            date: Date of the bulletin
            
        Returns:
            Path to bulletin .txt file
        """
        date_str = date.strftime("%Y-%m-%d")
        bulletin_path = self.output_dir / f"{date_str}.txt"
        return bulletin_path
    
    def read_bulletin(self, date: datetime) -> str:
        """
        Read bulletin text for a specific date
        
        Args:
            date: Date of the bulletin to read
            
        Returns:
            Bulletin text content
            
        Raises:
            FileNotFoundError: If bulletin file doesn't exist
            ValueError: If bulletin is empty
        """
        bulletin_path = self.get_bulletin_path(date)
        
        if not bulletin_path.exists():
            raise FileNotFoundError(
                f"Bulletin file not found for {date.strftime('%Y-%m-%d')}: {bulletin_path}"
            )
        
        logger.info(f"Reading bulletin from: {bulletin_path}")
        
        with open(bulletin_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            raise ValueError(f"Bulletin file is empty: {bulletin_path}")
        
        logger.info(f"Successfully read bulletin ({len(content)} characters)")
        return content
    
    def read_yesterday_bulletin(self) -> tuple[str, datetime]:
        """
        Read yesterday's bulletin
        
        Returns:
            Tuple of (bulletin_text, bulletin_date)
            
        Raises:
            FileNotFoundError: If yesterday's bulletin doesn't exist
        """
        yesterday = datetime.now() - timedelta(days=1)
        content = self.read_bulletin(yesterday)
        return content, yesterday
    
    def read_latest_bulletin(self) -> tuple[str, datetime]:
        """
        Read the most recent bulletin available
        
        Returns:
            Tuple of (bulletin_text, bulletin_date)
            
        Raises:
            FileNotFoundError: If no bulletins found
        """
        # Get all .txt files in output directory
        txt_files = sorted(self.output_dir.glob("*.txt"), reverse=True)
        
        if not txt_files:
            raise FileNotFoundError(
                f"No bulletin files found in {self.output_dir}"
            )
        
        # Try to read the most recent ones
        for txt_file in txt_files:
            try:
                # Extract date from filename (YYYY-MM-DD.txt)
                date_str = txt_file.stem
                date = datetime.strptime(date_str, "%Y-%m-%d")
                
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                
                if content:
                    logger.info(f"Found latest bulletin: {txt_file.name}")
                    return content, date
            except (ValueError, Exception) as e:
                logger.warning(f"Skipping invalid file {txt_file.name}: {e}")
                continue
        
        raise FileNotFoundError("No valid bulletin files found")
    
    def list_available_bulletins(self) -> list[datetime]:
        """
        List all available bulletin dates
        
        Returns:
            List of dates with available bulletins
        """
        txt_files = sorted(self.output_dir.glob("*.txt"))
        dates = []
        
        for txt_file in txt_files:
            try:
                date_str = txt_file.stem
                date = datetime.strptime(date_str, "%Y-%m-%d")
                dates.append(date)
            except ValueError:
                continue
        
        return dates
    
    def validate_bulletin(self, content: str) -> bool:
        """
        Validate bulletin content
        
        Args:
            content: Bulletin text to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not content or not content.strip():
            logger.error("Bulletin is empty")
            return False
        
        # Check if it's too short (likely incomplete)
        if len(content) < 100:
            logger.warning(f"Bulletin seems too short ({len(content)} chars)")
            return False
        
        # Check encoding
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            logger.error("Bulletin contains invalid UTF-8 characters")
            return False
        
        logger.info("Bulletin validation passed")
        return True
