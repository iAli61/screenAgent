"""
File Storage Service Implementation
Provides file storage operations using the storage strategy pattern
"""
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

from src.domain.interfaces.storage_service import IFileStorageService
from .storage_strategy import IStorageStrategy


class FileStorageService(IFileStorageService):
    """Concrete implementation of file storage service using storage strategies"""
    
    def __init__(self, storage_strategy: IStorageStrategy):
        self._storage_strategy = storage_strategy
        self._logger = logging.getLogger(__name__)
    
    async def save_file(
        self, 
        content: bytes, 
        filename: str,
        directory: Optional[Path] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Save file content to storage"""
        try:
            # Use storage strategy to save the file
            file_path = Path(directory or Path(".")) / filename
            
            # For now, delegate to the storage strategy's save method
            # This assumes the storage strategy can handle raw file content
            await asyncio.to_thread(
                self._storage_strategy.save_screenshot,
                str(file_path),
                content,
                metadata or {}
            )
            
            return file_path
            
        except Exception as e:
            self._logger.error(f"Failed to save file {filename}: {e}")
            raise
    
    async def get_file(self, file_path) -> Optional[bytes]:
        """Retrieve file content by path"""
        try:
            # Convert to Path object if it's a string or FilePath object
            if isinstance(file_path, str):
                path_obj = Path(file_path)
            elif hasattr(file_path, 'path'):  # FilePath object
                path_obj = Path(file_path.path)
            else:
                path_obj = file_path
                
            if path_obj.exists():
                return await asyncio.to_thread(path_obj.read_bytes)
            return None
            
        except Exception as e:
            self._logger.error(f"Failed to get file {file_path}: {e}")
            return None
    
    async def delete_file(self, file_path) -> bool:
        """Delete file from storage"""
        try:
            # Convert to Path object if it's a string or FilePath object
            if isinstance(file_path, str):
                path_obj = Path(file_path)
            elif hasattr(file_path, 'path'):  # FilePath object
                path_obj = Path(file_path.path)
            else:
                path_obj = file_path
                
            if path_obj.exists():
                await asyncio.to_thread(path_obj.unlink)
                self._logger.info(f"Deleted file: {path_obj}")
                return True
            else:
                self._logger.warning(f"File not found for deletion: {path_obj}")
            return False
            
        except Exception as e:
            self._logger.error(f"Failed to delete file {file_path}: {e}")
            return False
    
    async def file_exists(self, file_path) -> bool:
        """Check if file exists in storage"""
        try:
            # Convert to Path object if it's a string or FilePath object
            if isinstance(file_path, str):
                path_obj = Path(file_path)
            elif hasattr(file_path, 'path'):  # FilePath object
                path_obj = Path(file_path.path)
            else:
                path_obj = file_path
                
            return await asyncio.to_thread(path_obj.exists)
        except Exception as e:
            self._logger.error(f"Failed to check file existence {file_path}: {e}")
            return False
    
    async def list_files(
        self, 
        directory: Path,
        pattern: Optional[str] = None,
        recursive: bool = False
    ) -> List[Path]:
        """List files in directory"""
        try:
            if not directory.exists():
                return []
            
            if recursive:
                if pattern:
                    files = list(directory.rglob(pattern))
                else:
                    files = [f for f in directory.rglob("*") if f.is_file()]
            else:
                if pattern:
                    files = list(directory.glob(pattern))
                else:
                    files = [f for f in directory.iterdir() if f.is_file()]
            
            return files
            
        except Exception as e:
            self._logger.error(f"Failed to list files in {directory}: {e}")
            return []
    
    async def get_file_metadata(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get file metadata"""
        try:
            if not file_path.exists():
                return None
            
            stat = await asyncio.to_thread(file_path.stat)
            return {
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "name": file_path.name,
                "extension": file_path.suffix
            }
            
        except Exception as e:
            self._logger.error(f"Failed to get metadata for {file_path}: {e}")
            return None
    
    async def get_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Get file information (size, modified date, etc.)"""
        return await self.get_file_metadata(file_path)
    
    async def cleanup_old_files(
        self, 
        directory: Path,
        max_age_days: int = 30,
        pattern: Optional[str] = None
    ) -> int:
        """Clean up old files in directory"""
        try:
            if not directory.exists():
                return 0
            
            import time
            max_age_seconds = max_age_days * 24 * 60 * 60
            current_time = time.time()
            deleted_count = 0
            
            if pattern:
                files = list(directory.glob(pattern))
            else:
                files = [f for f in directory.iterdir() if f.is_file()]
            
            for file_path in files:
                try:
                    stat = await asyncio.to_thread(file_path.stat)
                    if current_time - stat.st_mtime > max_age_seconds:
                        await asyncio.to_thread(file_path.unlink)
                        deleted_count += 1
                        self._logger.debug(f"Deleted old file: {file_path}")
                except Exception as e:
                    self._logger.warning(f"Failed to delete old file {file_path}: {e}")
            
            return deleted_count
            
        except Exception as e:
            self._logger.error(f"Failed to cleanup old files in {directory}: {e}")
            return 0
    
    async def save_metadata(self, file_path, metadata: Dict[str, Any]) -> bool:
        """Save metadata to a JSON file"""
        try:
            import json
            
            # Convert to Path object if it's a string or FilePath object
            if isinstance(file_path, str):
                path_obj = Path(file_path)
            elif hasattr(file_path, 'path'):  # FilePath object
                path_obj = Path(file_path.path)
            else:
                path_obj = file_path
                
            # Ensure parent directory exists
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON data synchronously in thread
            def write_json():
                with open(path_obj, 'w') as f:
                    json.dump(metadata, f, indent=2)
                return True
                
            success = await asyncio.to_thread(write_json)
            if success:
                self._logger.info(f"Saved metadata to {path_obj}")
            return success
            
        except Exception as e:
            self._logger.error(f"Failed to save metadata to {file_path}: {e}")
            return False
