"""
Memory-based Screenshot Repository Implementation
Stores screenshots in memory for fast access and testing
"""
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from src.domain.repositories.screenshot_repository import IScreenshotRepository
from src.domain.entities.screenshot import Screenshot


logger = logging.getLogger(__name__)


class MemoryScreenshotRepository(IScreenshotRepository):
    """In-memory implementation of screenshot repository"""
    
    def __init__(self):
        self._screenshots: Dict[str, Screenshot] = {}
        self._lock = asyncio.Lock()
    
    async def create(self, screenshot: Screenshot) -> Screenshot:
        """Create a new screenshot record"""
        async with self._lock:
            if screenshot.id in self._screenshots:
                raise ValueError(f"Screenshot with ID {screenshot.id} already exists")
            
            self._screenshots[screenshot.id] = screenshot
            
            logger.debug(f"Created screenshot record in memory: {screenshot.id}")
            return screenshot
    
    async def get_by_id(self, screenshot_id: str) -> Optional[Screenshot]:
        """Get screenshot by ID"""
        async with self._lock:
            return self._screenshots.get(screenshot_id)
    
    async def update(self, screenshot: Screenshot) -> Screenshot:
        """Update existing screenshot record"""
        async with self._lock:
            if screenshot.id not in self._screenshots:
                raise ValueError(f"Screenshot with ID {screenshot.id} not found")
            
            self._screenshots[screenshot.id] = screenshot
            
            logger.debug(f"Updated screenshot record in memory: {screenshot.id}")
            return screenshot
    
    async def delete(self, screenshot_id: str) -> bool:
        """Delete screenshot by ID"""
        async with self._lock:
            if screenshot_id not in self._screenshots:
                return False
            
            del self._screenshots[screenshot_id]
            
            logger.debug(f"Deleted screenshot from memory: {screenshot_id}")
            return True
    
    async def list_all(
        self, 
        limit: Optional[int] = None, 
        offset: int = 0
    ) -> List[Screenshot]:
        """List all screenshots with pagination"""
        async with self._lock:
            screenshots = list(self._screenshots.values())
            # Sort by timestamp (newest first)
            screenshots.sort(key=lambda s: s.timestamp.value, reverse=True)
            
            # Apply pagination
            end_index = offset + limit if limit else None
            return screenshots[offset:end_index]
    
    async def find_by_session(self, session_id: str) -> List[Screenshot]:
        """Find screenshots by monitoring session ID"""
        async with self._lock:
            return [
                screenshot for screenshot in self._screenshots.values()
                if screenshot.metadata.get("session_id") == session_id
            ]
    
    async def find_by_roi(self, roi_id: str) -> List[Screenshot]:
        """Find screenshots by ROI region ID"""
        async with self._lock:
            return [
                screenshot for screenshot in self._screenshots.values()
                if screenshot.metadata.get("roi_id") == roi_id
            ]
    
    async def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Screenshot]:
        """Find screenshots within date range"""
        async with self._lock:
            return [
                screenshot for screenshot in self._screenshots.values()
                if start_date <= screenshot.timestamp.value <= end_date
            ]
    
    async def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Screenshot]:
        """Find screenshots matching criteria"""
        async with self._lock:
            results = []
            for screenshot in self._screenshots.values():
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
        async with self._lock:
            return len(self._screenshots)
    
    async def get_storage_size(self) -> int:
        """Get total storage size of all screenshots"""
        async with self._lock:
            return sum(screenshot.size_bytes for screenshot in self._screenshots.values())
    
    async def cleanup_older_than(self, max_age_days: int) -> int:
        """Clean up screenshots older than specified days"""
        async with self._lock:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            deleted_count = 0
            
            screenshots_to_delete = [
                screenshot_id for screenshot_id, screenshot in self._screenshots.items()
                if screenshot.timestamp.value < cutoff_date
            ]
            
            for screenshot_id in screenshots_to_delete:
                del self._screenshots[screenshot_id]
                deleted_count += 1
            
            logger.debug(f"Cleaned up {deleted_count} old screenshots from memory")
            return deleted_count
    
    async def clear_all(self) -> None:
        """Clear all screenshots from memory (for testing)"""
        async with self._lock:
            self._screenshots.clear()
            logger.debug("Cleared all screenshots from memory")
