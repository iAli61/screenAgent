"""
Memory-based Storage Strategy
Implements in-memory storage for screenshots with optional persistence
"""
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from .storage_strategy import IStorageStrategy
from ...domain.entities.screenshot import Screenshot
from ...domain.value_objects.timestamp import Timestamp


class MemoryStorageStrategy(IStorageStrategy):
    """In-memory storage implementation"""
    
    def __init__(self, max_screenshots: int = 100, persistence_file: Optional[str] = None):
        self.max_screenshots = max_screenshots
        self.persistence_file = Path(persistence_file) if persistence_file else None
        
        # In-memory storage
        self._screenshots: Dict[str, Screenshot] = {}
        self._order: List[str] = []  # Maintain insertion order
        
        # Load from persistence if available
        if self.persistence_file:
            asyncio.create_task(self._load_from_persistence())
    
    async def store(self, screenshot: Screenshot) -> bool:
        """Store screenshot in memory"""
        try:
            screenshot_id = screenshot.id
            
            # Store screenshot
            self._screenshots[screenshot_id] = screenshot
            
            # Update order
            if screenshot_id in self._order:
                self._order.remove(screenshot_id)
            self._order.append(screenshot_id)
            
            # Enforce limits
            await self._enforce_limits()
            
            # Persist if configured
            if self.persistence_file:
                await self._save_to_persistence()
            
            return True
            
        except Exception as e:
            print(f"Error storing screenshot {screenshot.id}: {e}")
            return False
    
    async def retrieve(self, screenshot_id: str) -> Optional[Screenshot]:
        """Retrieve screenshot from memory"""
        return self._screenshots.get(screenshot_id)
    
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Screenshot]:
        """List all screenshots with pagination"""
        try:
            # Get ordered list (newest first)
            ordered_ids = list(reversed(self._order))
            
            # Apply pagination
            if offset > 0:
                ordered_ids = ordered_ids[offset:]
            if limit:
                ordered_ids = ordered_ids[:limit]
            
            # Return screenshots
            return [
                self._screenshots[screenshot_id]
                for screenshot_id in ordered_ids
                if screenshot_id in self._screenshots
            ]
            
        except Exception as e:
            print(f"Error listing screenshots: {e}")
            return []
    
    async def delete(self, screenshot_id: str) -> bool:
        """Delete a screenshot by ID"""
        try:
            if screenshot_id not in self._screenshots:
                return False
            
            # Remove from storage and order
            del self._screenshots[screenshot_id]
            if screenshot_id in self._order:
                self._order.remove(screenshot_id)
            
            # Persist changes
            if self.persistence_file:
                await self._save_to_persistence()
            
            return True
            
        except Exception as e:
            print(f"Error deleting screenshot {screenshot_id}: {e}")
            return False
    
    async def delete_all(self) -> bool:
        """Delete all screenshots"""
        try:
            self._screenshots.clear()
            self._order.clear()
            
            # Clear persistence
            if self.persistence_file and self.persistence_file.exists():
                self.persistence_file.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error deleting all screenshots: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            total_size = sum(len(screenshot.data) for screenshot in self._screenshots.values())
            
            oldest_timestamp = None
            newest_timestamp = None
            
            if self._screenshots:
                timestamps = [screenshot.timestamp for screenshot in self._screenshots.values()]
                oldest_timestamp = min(timestamps)
                newest_timestamp = max(timestamps)
            
            return {
                'type': 'memory',
                'total_screenshots': len(self._screenshots),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'oldest_screenshot': oldest_timestamp.isoformat() if oldest_timestamp else None,
                'newest_screenshot': newest_timestamp.isoformat() if newest_timestamp else None,
                'max_screenshots': self.max_screenshots,
                'persistence_enabled': self.persistence_file is not None
            }
            
        except Exception as e:
            print(f"Error getting storage stats: {e}")
            return {'type': 'memory', 'error': str(e)}
    
    async def cleanup_old(self, max_age_hours: int) -> int:
        """Cleanup screenshots older than specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            deleted_count = 0
            
            to_delete = []
            for screenshot_id, screenshot in self._screenshots.items():
                if screenshot.timestamp < cutoff_time:
                    to_delete.append(screenshot_id)
            
            for screenshot_id in to_delete:
                if await self.delete(screenshot_id):
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            return 0
    
    async def _enforce_limits(self):
        """Enforce screenshot count limits"""
        while len(self._order) > self.max_screenshots:
            # Remove oldest screenshot
            oldest_id = self._order.pop(0)
            if oldest_id in self._screenshots:
                del self._screenshots[oldest_id]
    
    async def _save_to_persistence(self):
        """Save metadata to persistence file (metadata only, not data)"""
        if not self.persistence_file:
            return
        
        try:
            metadata_list = []
            for screenshot_id in self._order:
                if screenshot_id in self._screenshots:
                    screenshot = self._screenshots[screenshot_id]
                    metadata_list.append({
                        'id': screenshot.id,
                        'timestamp': screenshot.timestamp.isoformat(),
                        'width': screenshot.width,
                        'height': screenshot.height,
                        'format': screenshot.format,
                        'metadata': screenshot.metadata
                    })
            
            persistence_data = {
                'version': '1.0',
                'timestamp': datetime.now().isoformat(),
                'screenshots': metadata_list
            }
            
            # Ensure directory exists
            self.persistence_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.persistence_file.write_text(
                    json.dumps(persistence_data, indent=2)
                )
            )
            
        except Exception as e:
            print(f"Error saving to persistence: {e}")
    
    async def _load_from_persistence(self):
        """Load metadata from persistence file"""
        if not self.persistence_file or not self.persistence_file.exists():
            return
        
        try:
            # Load persistence data
            persistence_data = json.loads(self.persistence_file.read_text())
            
            # Note: We only load metadata, not actual screenshot data
            # This is intentional - screenshot data is ephemeral in memory storage
            print(f"📋 Loaded {len(persistence_data.get('screenshots', []))} screenshot metadata entries from persistence")
            
        except Exception as e:
            print(f"Error loading from persistence: {e}")
