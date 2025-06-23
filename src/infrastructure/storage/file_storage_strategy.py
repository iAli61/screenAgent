"""
File-based Storage Strategy
Implements file system storage for screenshots
"""
import os
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from .storage_strategy import IStorageStrategy
from ...domain.entities.screenshot import Screenshot
from ...domain.value_objects.timestamp import Timestamp
from ...domain.value_objects.file_path import FilePath
from ...domain.value_objects.coordinates import Coordinates


class FileStorageStrategy(IStorageStrategy):
    """File-based storage implementation"""
    
    def __init__(self, base_path: str = "screenshots", max_screenshots: int = 1000):
        self.base_path = Path(base_path)
        self.max_screenshots = max_screenshots
        self.metadata_file = self.base_path / "metadata.json"
        
        # Ensure directory exists
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Load existing metadata
        self._metadata: Dict[str, Dict[str, Any]] = self._load_metadata()
    
    async def store(self, screenshot: Screenshot) -> bool:
        """Store screenshot to file system"""
        try:
            # Create filename based on timestamp and ID
            filename = f"{screenshot.id}.png"
            file_path = self.base_path / "images" / filename
            
            # Create directories if needed
            image_dir = self.base_path / "images"
            image_dir.mkdir(parents=True, exist_ok=True)
            
            print(f"💾 Saving screenshot to {file_path}")
            
            # Store image data
            with open(file_path, 'wb') as f:
                f.write(screenshot.data)
            
            print(f"✅ Screenshot saved successfully ({len(screenshot.data)} bytes)")
            
            # Update metadata
            self._metadata[screenshot.id] = {
                'id': screenshot.id,
                'timestamp': screenshot.timestamp.value.isoformat(),
                'filename': filename,
                'file_path': str(file_path),
                'width': screenshot.width,
                'height': screenshot.height,
                'format': screenshot.format,
                'roi_x': screenshot.roi.x if screenshot.roi else None,
                'roi_y': screenshot.roi.y if screenshot.roi else None,
                'roi_width': screenshot.roi.width if screenshot.roi else None,
                'roi_height': screenshot.roi.height if screenshot.roi else None,
                'metadata': screenshot.metadata
            }
            
            # Save metadata
            await self._save_metadata()
            
            # Enforce storage limits
            await self._enforce_limits()
            
            return True
            
        except Exception as e:
            print(f"❌ Error storing screenshot {screenshot.id}: {e}")
            return False
    
    async def retrieve(self, screenshot_id: str) -> Optional[Screenshot]:
        """Retrieve screenshot from file system"""
        try:
            if screenshot_id not in self._metadata:
                return None
            
            meta = self._metadata[screenshot_id]
            file_path = Path(meta['file_path'])
            
            if not file_path.exists():
                # Clean up stale metadata
                del self._metadata[screenshot_id]
                await self._save_metadata()
                return None
            
            # Load image data
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Reconstruct coordinates if ROI exists
            roi = None
            if meta.get('roi_x') is not None:
                roi = Coordinates(
                    x=meta['roi_x'],
                    y=meta['roi_y'],
                    width=meta['roi_width'],
                    height=meta['roi_height']
                )
            
            # Create screenshot object
            screenshot = Screenshot(
                id=meta['id'],
                timestamp=Timestamp(datetime.fromisoformat(meta['timestamp'])),
                data=data,
                width=meta['width'],
                height=meta['height'],
                format=meta['format'],
                file_path=FilePath(meta['file_path']),
                roi=roi,
                metadata=meta.get('metadata', {})
            )
            
            return screenshot
            
        except Exception as e:
            print(f"Error retrieving screenshot {screenshot_id}: {e}")
            return None
    
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Screenshot]:
        """List all screenshots with pagination"""
        try:
            # Sort by timestamp (newest first)
            sorted_ids = sorted(
                self._metadata.keys(),
                key=lambda x: self._metadata[x]['timestamp'],
                reverse=True
            )
            
            # Apply pagination
            if offset > 0:
                sorted_ids = sorted_ids[offset:]
            if limit:
                sorted_ids = sorted_ids[:limit]
            
            # Retrieve screenshots
            screenshots = []
            for screenshot_id in sorted_ids:
                screenshot = await self.retrieve(screenshot_id)
                if screenshot:
                    screenshots.append(screenshot)
            
            return screenshots
            
        except Exception as e:
            print(f"Error listing screenshots: {e}")
            return []
    
    async def delete(self, screenshot_id: str) -> bool:
        """Delete a screenshot by ID"""
        try:
            if screenshot_id not in self._metadata:
                return False
            
            meta = self._metadata[screenshot_id]
            file_path = Path(meta['file_path'])
            
            # Delete file if it exists
            if file_path.exists():
                file_path.unlink()
            
            # Remove from metadata
            del self._metadata[screenshot_id]
            await self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error deleting screenshot {screenshot_id}: {e}")
            return False
    
    async def delete_all(self) -> bool:
        """Delete all screenshots"""
        try:
            # Delete all files
            for meta in self._metadata.values():
                file_path = Path(meta['file_path'])
                if file_path.exists():
                    file_path.unlink()
            
            # Clear metadata
            self._metadata.clear()
            await self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error deleting all screenshots: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            total_size = 0
            file_count = 0
            
            for meta in self._metadata.values():
                file_path = Path(meta['file_path'])
                if file_path.exists():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            oldest_timestamp = None
            newest_timestamp = None
            
            if self._metadata:
                timestamps = [
                    datetime.fromisoformat(meta['timestamp'])
                    for meta in self._metadata.values()
                ]
                oldest_timestamp = min(timestamps)
                newest_timestamp = max(timestamps)
            
            return {
                'type': 'file',
                'total_screenshots': len(self._metadata),
                'files_on_disk': file_count,
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'base_path': str(self.base_path),
                'oldest_screenshot': oldest_timestamp.isoformat() if oldest_timestamp else None,
                'newest_screenshot': newest_timestamp.isoformat() if newest_timestamp else None,
                'max_screenshots': self.max_screenshots
            }
            
        except Exception as e:
            print(f"Error getting storage stats: {e}")
            return {'type': 'file', 'error': str(e)}
    
    async def cleanup_old(self, max_age_hours: int) -> int:
        """Cleanup screenshots older than specified hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            deleted_count = 0
            
            to_delete = []
            for screenshot_id, meta in self._metadata.items():
                timestamp = datetime.fromisoformat(meta['timestamp'])
                if timestamp < cutoff_time:
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
        if len(self._metadata) <= self.max_screenshots:
            return
        
        # Sort by timestamp (oldest first)
        sorted_ids = sorted(
            self._metadata.keys(),
            key=lambda x: self._metadata[x]['timestamp']
        )
        
        # Delete oldest screenshots
        to_delete = sorted_ids[:len(sorted_ids) - self.max_screenshots]
        for screenshot_id in to_delete:
            await self.delete(screenshot_id)
    
    def _load_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Load metadata from file"""
        try:
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
        
        return {}
    
    async def _save_metadata(self):
        """Save metadata to file"""
        try:
            # Use asyncio to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                None, 
                self._save_metadata_sync
            )
        except Exception as e:
            print(f"Error saving metadata: {e}")
    
    def _save_metadata_sync(self):
        """Synchronous metadata save"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self._metadata, f, indent=2)
    
    def save_screenshot(self, file_path: str, content: bytes, metadata: Dict[str, Any] = None) -> bool:
        """Save screenshot data to a file
        
        Args:
            file_path: Path where to save the screenshot
            content: Binary content of the screenshot
            metadata: Optional metadata
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write binary content to file
            with open(path, 'wb') as f:
                f.write(content)
                
            print(f"✅ Saved screenshot to {file_path} ({len(content)} bytes)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save file {file_path}: {e}")
            return False
