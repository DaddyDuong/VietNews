"""
File Manager - Manages output files and organization
"""
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class FileManager:
    """Manages output file organization and cleanup"""
    
    def __init__(self, output_dir: Path):
        """
        Initialize file manager
        
        Args:
            output_dir: Directory for output files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def save_audio_file(
        self,
        source_path: Path,
        target_date: datetime,
        filename_format: str = "{date}.wav"
    ) -> Optional[Path]:
        """
        Save audio file with proper naming
        
        Args:
            source_path: Source audio file path
            target_date: Date for filename
            filename_format: Format string for filename
            
        Returns:
            Path to saved file or None if failed
        """
        try:
            # Generate target filename
            date_str = target_date.strftime("%Y-%m-%d")
            target_filename = filename_format.format(date=date_str)
            target_path = self.output_dir / target_filename
            
            # Check if source exists
            if not source_path.exists():
                logger.error(f"Source file not found: {source_path}")
                return None
            
            # Copy file
            logger.info(f"Saving audio file: {source_path} → {target_path}")
            shutil.copy2(source_path, target_path)
            
            # Verify copy
            if target_path.exists():
                logger.info(f"✓ Audio saved: {target_path}")
                return target_path
            else:
                logger.error("File copy failed")
                return None
                
        except Exception as e:
            logger.error(f"Failed to save audio file: {e}")
            return None
    
    def cleanup_download_file(self, filepath: Path) -> bool:
        """
        Clean up temporary download file
        
        Args:
            filepath: Path to file to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Cleaned up: {filepath}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cleanup file: {e}")
            return False
    
    def list_output_files(self) -> list[Path]:
        """
        List all output audio files
        
        Returns:
            List of audio file paths
        """
        audio_extensions = ['.wav', '.mp3', '.ogg', '.m4a']
        files = []
        
        for ext in audio_extensions:
            files.extend(self.output_dir.glob(f"*{ext}"))
        
        return sorted(files)
    
    def get_output_path(self, date: datetime, extension: str = ".wav") -> Path:
        """
        Get output path for a specific date
        
        Args:
            date: Target date
            extension: File extension
            
        Returns:
            Path to output file
        """
        date_str = date.strftime("%Y-%m-%d")
        filename = f"{date_str}{extension}"
        return self.output_dir / filename
    
    def file_exists_for_date(self, date: datetime) -> bool:
        """
        Check if output file exists for a date
        
        Args:
            date: Date to check
            
        Returns:
            True if file exists
        """
        date_str = date.strftime("%Y-%m-%d")
        
        # Check for various audio formats
        for ext in ['.wav', '.mp3', '.ogg', '.m4a']:
            filepath = self.output_dir / f"{date_str}{ext}"
            if filepath.exists():
                return True
        
        return False
    
    def get_file_info(self, filepath: Path) -> dict:
        """
        Get information about a file
        
        Args:
            filepath: Path to file
            
        Returns:
            Dict with file information
        """
        if not filepath.exists():
            return {'exists': False}
        
        stat = filepath.stat()
        
        return {
            'exists': True,
            'path': str(filepath),
            'size': stat.st_size,
            'size_mb': stat.st_size / (1024 * 1024),
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
        }
