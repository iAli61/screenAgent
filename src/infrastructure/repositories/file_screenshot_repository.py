"""
File-based Screenshot Repository Implementation
Stores screenshots as files with JSON metadata
"""
import json
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import logging

from src.domain.repositories.screenshot_repository import IScreenshotRepository
from src.domain.entities.screenshot import Screenshot
from src.domain.value_objects.timestamp import Timestamp
from src.domain.value_objects.file_path import FilePath


logger = logging.getLogger(__name__)


class FileScreenshotRepository(IScreenshotRepository):
    """File-based implementation of screenshot repository"""
    
    def __init__(self, storage_directory: Path):
        self.storage_directory = Path(storage_directory)
        self.metadata_directory = self.storage_directory / "metadata"
        self.images_directory = self.storage_directory / "images"
        
        # Ensure directories exist
        self.metadata_directory.mkdir(parents=True, exist_ok=True)
        self.images_directory.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for quick access
        self._cache: Dict[str, Screenshot] = {}
        self._cache_loaded = False
    
    async def _ensure_cache_loaded(self):
        """Ensure metadata cache is loaded"""
        if not self._cache_loaded:
            await self._load_cache()
    
    async def _load_cache(self):
        """Load all metadata into cache"""
        try:
            for metadata_file in self.metadata_directory.glob("*.json"):
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    screenshot = self._dict_to_screenshot(data)
                    self._cache[screenshot.id] = screenshot
            
            self._cache_loaded = True
            logger.info(f"Loaded {len(self._cache)} screenshots into cache")
            
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            self._cache = {}
    
    async def _save_metadata(self, screenshot: Screenshot):
        """Save screenshot metadata to file"""
        try:
            metadata_file = self.metadata_directory / f"{screenshot.id}.json"
            data = self._screenshot_to_dict(screenshot)
            
            with open(metadata_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            # Update cache
            self._cache[screenshot.id] = screenshot
            
        except Exception as e:
            logger.error(f"Failed to save metadata for {screenshot.id}: {e}")
            raise
    
    def _screenshot_to_dict(self, screenshot: Screenshot) -> Dict[str, Any]:
        """Convert screenshot entity to dictionary"""
        return {
            "id": screenshot.id,
            "file_path": str(screenshot.file_path.path),
            "timestamp": screenshot.timestamp.value.isoformat(),
            "width": screenshot.width,
            "height": screenshot.height,
            "format": screenshot.format,
            "size_bytes": screenshot.size_bytes,
            "metadata": screenshot.metadata
        }
    
    def _dict_to_screenshot(self, data: Dict[str, Any]) -> Screenshot:
        """Convert dictionary to screenshot entity"""
        return Screenshot(
            id=data["id"],
            file_path=FilePath(data["file_path"]),
            timestamp=Timestamp(datetime.fromisoformat(data["timestamp"])),
            width=data["width"],
            height=data["height"],
            format=data["format"],
            size_bytes=data["size_bytes"],
            metadata=data.get("metadata", {})
        )
    
    async def create(self, screenshot: Screenshot) -> Screenshot:
        """Create a new screenshot record"""
        await self._ensure_cache_loaded()
        
        if screenshot.id in self._cache:
            raise ValueError(f"Screenshot with ID {screenshot.id} already exists")
        
        await self._save_metadata(screenshot)
        
        logger.info(f"Created screenshot record: {screenshot.id}")
        return screenshot
    
    async def get_by_id(self, screenshot_id: str) -> Optional[Screenshot]:
        """Get screenshot by ID"""
        await self._ensure_cache_loaded()
        return self._cache.get(screenshot_id)
    
    async def update(self, screenshot: Screenshot) -> Screenshot:
        """Update existing screenshot record"""
        await self._ensure_cache_loaded()
        
        if screenshot.id not in self._cache:
            raise ValueError(f"Screenshot with ID {screenshot.id} not found")
        
        await self._save_metadata(screenshot)
        
        logger.info(f"Updated screenshot record: {screenshot.id}")
        return screenshot
    
    async def delete(self, screenshot_id: str) -> bool:
        """Delete screenshot by ID"""
        await self._ensure_cache_loaded()
        
        if screenshot_id not in self._cache:
            return False
        
        try:
            # Delete metadata file
            metadata_file = self.metadata_directory / f"{screenshot_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()
            
            # Delete image file if it exists
            screenshot = self._cache[screenshot_id]
            
            try:
                # Try to get screenshot path
                file_path = screenshot.file_path
                
                if file_path is None:
                    logger.warning(f"No file path for screenshot {screenshot_id}")
                elif isinstance(file_path, str):
                    # It's a string path
                    path_obj = Path(file_path)
                    if path_obj.exists():
                        path_obj.unlink()
                        logger.info(f"Deleted image file: {file_path}")
                elif hasattr(file_path, 'path') and hasattr(file_path, 'exists'):
                    # It's a FilePath object
                    if file_path.exists:
                        file_path.unlink()
                        logger.info(f"Deleted image file: {file_path.path}")
                else:
                    # Unknown type
                    logger.warning(f"Unknown file_path type: {type(file_path)}")
                
                # Also try deleting from the images directory
                image_file = self.images_directory / f"{screenshot_id}.png"
                if image_file.exists():
                    image_file.unlink()
                    logger.info(f"Deleted image file: {image_file}")
                
            except Exception as e:
                logger.error(f"Error deleting image file: {e}")
            
            # Remove from cache
            del self._cache[screenshot_id]
            
            logger.info(f"Deleted screenshot: {screenshot_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete screenshot {screenshot_id}: {e}")
            return False
    
    async def list_all(
        self, 
        limit: Optional[int] = None, 
        offset: int = 0
    ) -> List[Screenshot]:
        """List all screenshots with pagination"""
        await self._ensure_cache_loaded()
        
        screenshots = list(self._cache.values())
        # Sort by timestamp (newest first)
        screenshots.sort(key=lambda s: s.timestamp.value, reverse=True)
        
        # Apply pagination
        end_index = offset + limit if limit else None
        return screenshots[offset:end_index]
    
    async def find_by_session(self, session_id: str) -> List[Screenshot]:
        """Find screenshots by monitoring session ID"""
        await self._ensure_cache_loaded()
        
        return [
            screenshot for screenshot in self._cache.values()
            if screenshot.metadata.get("session_id") == session_id
        ]
    
    async def find_by_roi(self, roi_id: str) -> List[Screenshot]:
        """Find screenshots by ROI region ID"""
        await self._ensure_cache_loaded()
        
        return [
            screenshot for screenshot in self._cache.values()
            if screenshot.metadata.get("roi_id") == roi_id
        ]
    
    async def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Screenshot]:
        """Find screenshots within date range"""
        await self._ensure_cache_loaded()
        
        return [
            screenshot for screenshot in self._cache.values()
            if start_date <= screenshot.timestamp.value <= end_date
        ]
    
    async def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Screenshot]:
        """Find screenshots matching criteria"""
        await self._ensure_cache_loaded()
        
        results = []
        for screenshot in self._cache.values():
            match = True
            
            for key, value in criteria.items():
                if key == "session_id":
                    if screenshot.metadata.get("session_id") != value:
                        match = False
                        break
                elif key == "roi_id":
                    if screenshot.metadata.get("roi_id") != value:
                        match = False
                        break
                elif key == "format":
                    if screenshot.format != value:
                        match = False
                        break
                elif key == "min_size":
                    if screenshot.size_bytes < value:
                        match = False
                        break
                elif key == "max_size":
                    if screenshot.size_bytes > value:
                        match = False
                        break
            
            if match:
                results.append(screenshot)
        
        return results
    
    async def get_total_count(self) -> int:
        """Get total count of screenshots"""
        await self._ensure_cache_loaded()
        return len(self._cache)
    
    async def get_storage_size(self) -> int:
        """Get total storage size of all screenshots"""
        await self._ensure_cache_loaded()
        return sum(screenshot.size_bytes for screenshot in self._cache.values())
    
    async def cleanup_older_than(self, max_age_days: int) -> int:
        """Clean up screenshots older than specified days"""
        await self._ensure_cache_loaded()
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0
        
        screenshots_to_delete = [
            screenshot for screenshot in self._cache.values()
            if screenshot.timestamp.value < cutoff_date
        ]
        
        for screenshot in screenshots_to_delete:
            if await self.delete(screenshot.id):
                deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old screenshots")
        return deleted_count
