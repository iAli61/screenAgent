"""
Storage management for screenshots and metadata
Part of Phase 1.4 - Screenshot Manager Module Refactoring
"""
import os
import json
import base64
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import threading


@dataclass
class ScreenshotMetadata:
    """Screenshot metadata structure"""
    id: str
    timestamp: float
    timestamp_formatted: str
    size: int
    roi: tuple
    capture_method: str
    change_score: float = 0.0
    confidence: float = 0.0
    tags: List[str] = None
    analysis_results: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.analysis_results is None:
            self.analysis_results = {}


@dataclass
class ScreenshotData:
    """Complete screenshot data with metadata"""
    metadata: ScreenshotMetadata
    data: bytes
    
    @property
    def id(self) -> str:
        return self.metadata.id
    
    @property
    def timestamp(self) -> float:
        return self.metadata.timestamp
    
    @property
    def size(self) -> int:
        return len(self.data)


class ScreenshotStorage:
    """Abstract storage interface for screenshots"""
    
    def store_screenshot(self, screenshot: ScreenshotData) -> bool:
        """Store a screenshot with metadata"""
        raise NotImplementedError
    
    def retrieve_screenshot(self, screenshot_id: str) -> Optional[ScreenshotData]:
        """Retrieve a screenshot by ID"""
        raise NotImplementedError
    
    def list_screenshots(self, limit: Optional[int] = None) -> List[ScreenshotMetadata]:
        """List screenshot metadata"""
        raise NotImplementedError
    
    def delete_screenshot(self, screenshot_id: str) -> bool:
        """Delete a screenshot"""
        raise NotImplementedError
    
    def clear_all(self) -> bool:
        """Clear all screenshots"""
        raise NotImplementedError
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        raise NotImplementedError


class MemoryScreenshotStorage(ScreenshotStorage):
    """In-memory screenshot storage with optional persistence"""
    
    def __init__(self, max_screenshots: int = 100, persistence_file: Optional[str] = None):
        self.max_screenshots = max_screenshots
        self.persistence_file = persistence_file
        self._screenshots: Dict[str, ScreenshotData] = {}
        self._metadata_index: List[str] = []  # Ordered list of IDs
        self._lock = threading.RLock()
        
        # Load from persistence if available
        if persistence_file:
            self._load_from_persistence()
    
    def store_screenshot(self, screenshot: ScreenshotData) -> bool:
        """Store a screenshot in memory"""
        try:
            with self._lock:
                screenshot_id = screenshot.id
                
                # Update size to actual data size
                screenshot.metadata.size = len(screenshot.data)
                
                # Store screenshot
                self._screenshots[screenshot_id] = screenshot
                
                # Update index
                if screenshot_id in self._metadata_index:
                    self._metadata_index.remove(screenshot_id)
                self._metadata_index.append(screenshot_id)
                
                # Enforce size limit
                self._enforce_size_limit()
                
                # Persist if configured
                if self.persistence_file:
                    self._save_to_persistence()
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to store screenshot: {e}")
            return False
    
    def retrieve_screenshot(self, screenshot_id: str) -> Optional[ScreenshotData]:
        """Retrieve a screenshot by ID"""
        with self._lock:
            return self._screenshots.get(screenshot_id)
    
    def list_screenshots(self, limit: Optional[int] = None) -> List[ScreenshotMetadata]:
        """List screenshot metadata in chronological order"""
        with self._lock:
            screenshot_ids = self._metadata_index.copy()
            
            if limit:
                screenshot_ids = screenshot_ids[-limit:]
            
            return [
                self._screenshots[sid].metadata 
                for sid in screenshot_ids 
                if sid in self._screenshots
            ]
    
    def delete_screenshot(self, screenshot_id: str) -> bool:
        """Delete a screenshot"""
        try:
            with self._lock:
                if screenshot_id in self._screenshots:
                    del self._screenshots[screenshot_id]
                    
                if screenshot_id in self._metadata_index:
                    self._metadata_index.remove(screenshot_id)
                
                # Persist changes
                if self.persistence_file:
                    self._save_to_persistence()
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to delete screenshot: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all screenshots"""
        try:
            with self._lock:
                self._screenshots.clear()
                self._metadata_index.clear()
                
                # Clear persistence
                if self.persistence_file and os.path.exists(self.persistence_file):
                    os.remove(self.persistence_file)
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to clear screenshots: {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        with self._lock:
            total_size = sum(len(ss.data) for ss in self._screenshots.values())
            
            return {
                'count': len(self._screenshots),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'max_screenshots': self.max_screenshots,
                'oldest_timestamp': min(
                    (ss.timestamp for ss in self._screenshots.values()), 
                    default=0
                ),
                'newest_timestamp': max(
                    (ss.timestamp for ss in self._screenshots.values()), 
                    default=0
                ),
                'persistence_enabled': self.persistence_file is not None
            }
    
    def _enforce_size_limit(self):
        """Remove oldest screenshots if over limit"""
        while len(self._metadata_index) > self.max_screenshots:
            oldest_id = self._metadata_index.pop(0)
            if oldest_id in self._screenshots:
                del self._screenshots[oldest_id]
    
    def _save_to_persistence(self):
        """Save metadata to persistence file (not data, just metadata)"""
        if not self.persistence_file:
            return
        
        try:
            metadata_list = [
                asdict(self._screenshots[sid].metadata)
                for sid in self._metadata_index
                if sid in self._screenshots
            ]
            
            persistence_data = {
                'version': '1.0',
                'timestamp': time.time(),
                'screenshots': metadata_list
            }
            
            os.makedirs(os.path.dirname(self.persistence_file), exist_ok=True)
            with open(self.persistence_file, 'w') as f:
                json.dump(persistence_data, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Failed to save persistence: {e}")
    
    def _load_from_persistence(self):
        """Load metadata from persistence file"""
        if not self.persistence_file or not os.path.exists(self.persistence_file):
            return
        
        try:
            with open(self.persistence_file, 'r') as f:
                persistence_data = json.load(f)
            
            # Note: We only load metadata, not actual screenshot data
            # This is intentional - screenshot data is ephemeral
            print(f"📋 Loaded {len(persistence_data.get('screenshots', []))} screenshot metadata entries from persistence")
            
        except Exception as e:
            print(f"⚠️  Failed to load persistence: {e}")


class FileSystemScreenshotStorage(ScreenshotStorage):
    """File system-based screenshot storage"""
    
    def __init__(self, storage_dir: str, max_screenshots: int = 100):
        self.storage_dir = storage_dir
        self.max_screenshots = max_screenshots
        self.metadata_file = os.path.join(storage_dir, 'metadata.json')
        self._lock = threading.RLock()
        
        # Ensure storage directory exists
        os.makedirs(storage_dir, exist_ok=True)
        
        # Load existing metadata
        self._metadata_index = self._load_metadata_index()
    
    def store_screenshot(self, screenshot: ScreenshotData) -> bool:
        """Store screenshot to file system"""
        try:
            with self._lock:
                screenshot_id = screenshot.id
                
                # Save screenshot data
                screenshot_file = os.path.join(self.storage_dir, f"{screenshot_id}.png")
                with open(screenshot_file, 'wb') as f:
                    f.write(screenshot.data)
                
                # Update metadata
                self._metadata_index[screenshot_id] = screenshot.metadata
                
                # Enforce size limit
                self._enforce_size_limit()
                
                # Save metadata index
                self._save_metadata_index()
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to store screenshot to file system: {e}")
            return False
    
    def retrieve_screenshot(self, screenshot_id: str) -> Optional[ScreenshotData]:
        """Retrieve screenshot from file system"""
        try:
            with self._lock:
                if screenshot_id not in self._metadata_index:
                    return None
                
                screenshot_file = os.path.join(self.storage_dir, f"{screenshot_id}.png")
                if not os.path.exists(screenshot_file):
                    # Clean up orphaned metadata
                    del self._metadata_index[screenshot_id]
                    self._save_metadata_index()
                    return None
                
                with open(screenshot_file, 'rb') as f:
                    data = f.read()
                
                metadata = self._metadata_index[screenshot_id]
                return ScreenshotData(metadata=metadata, data=data)
                
        except Exception as e:
            print(f"❌ Failed to retrieve screenshot: {e}")
            return None
    
    def list_screenshots(self, limit: Optional[int] = None) -> List[ScreenshotMetadata]:
        """List screenshot metadata"""
        with self._lock:
            metadata_list = list(self._metadata_index.values())
            metadata_list.sort(key=lambda x: x.timestamp)
            
            if limit:
                metadata_list = metadata_list[-limit:]
            
            return metadata_list
    
    def delete_screenshot(self, screenshot_id: str) -> bool:
        """Delete screenshot from file system"""
        try:
            with self._lock:
                # Delete file
                screenshot_file = os.path.join(self.storage_dir, f"{screenshot_id}.png")
                if os.path.exists(screenshot_file):
                    os.remove(screenshot_file)
                
                # Remove from metadata
                if screenshot_id in self._metadata_index:
                    del self._metadata_index[screenshot_id]
                    self._save_metadata_index()
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to delete screenshot: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all screenshots"""
        try:
            with self._lock:
                # Delete all screenshot files
                for screenshot_id in list(self._metadata_index.keys()):
                    screenshot_file = os.path.join(self.storage_dir, f"{screenshot_id}.png")
                    if os.path.exists(screenshot_file):
                        os.remove(screenshot_file)
                
                # Clear metadata
                self._metadata_index.clear()
                self._save_metadata_index()
                
                return True
                
        except Exception as e:
            print(f"❌ Failed to clear all screenshots: {e}")
            return False
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        with self._lock:
            total_size = 0
            for screenshot_id in self._metadata_index:
                screenshot_file = os.path.join(self.storage_dir, f"{screenshot_id}.png")
                if os.path.exists(screenshot_file):
                    total_size += os.path.getsize(screenshot_file)
            
            return {
                'count': len(self._metadata_index),
                'total_size_bytes': total_size,
                'total_size_mb': total_size / (1024 * 1024),
                'storage_dir': self.storage_dir,
                'max_screenshots': self.max_screenshots
            }
    
    def _load_metadata_index(self) -> Dict[str, ScreenshotMetadata]:
        """Load metadata index from file"""
        if not os.path.exists(self.metadata_file):
            return {}
        
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
            
            metadata_index = {}
            for item in data.get('screenshots', []):
                metadata = ScreenshotMetadata(**item)
                metadata_index[metadata.id] = metadata
            
            return metadata_index
            
        except Exception as e:
            print(f"⚠️  Failed to load metadata index: {e}")
            return {}
    
    def _save_metadata_index(self):
        """Save metadata index to file"""
        try:
            data = {
                'version': '1.0',
                'timestamp': time.time(),
                'screenshots': [asdict(metadata) for metadata in self._metadata_index.values()]
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            print(f"❌ Failed to save metadata index: {e}")
    
    def _enforce_size_limit(self):
        """Remove oldest screenshots if over limit"""
        if len(self._metadata_index) <= self.max_screenshots:
            return
        
        # Sort by timestamp and remove oldest
        sorted_items = sorted(self._metadata_index.items(), key=lambda x: x[1].timestamp)
        
        for screenshot_id, _ in sorted_items[:-self.max_screenshots]:
            self.delete_screenshot(screenshot_id)


class StorageFactory:
    """Factory for creating storage instances"""
    
    @staticmethod
    def create_memory_storage(max_screenshots: int = 100, 
                            persistence_file: Optional[str] = None) -> MemoryScreenshotStorage:
        """Create memory-based storage"""
        return MemoryScreenshotStorage(max_screenshots, persistence_file)
    
    @staticmethod
    def create_filesystem_storage(storage_dir: str, 
                                max_screenshots: int = 100) -> FileSystemScreenshotStorage:
        """Create file system-based storage"""
        return FileSystemScreenshotStorage(storage_dir, max_screenshots)
    
    @staticmethod
    def create_default_storage(config) -> ScreenshotStorage:
        """Create default storage based on configuration"""
        import uuid
        import time
        
        storage_type = config.get('storage_type', 'memory')
        max_screenshots = config.get('max_screenshots', 100)
        
        if storage_type == 'filesystem':
            base_storage_dir = config.get('screenshot_dir', 'screenshots')
            
            # Create unique run directory to avoid conflicts between app runs
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            run_dir_name = f"run_{timestamp}_{unique_id}"
            
            # Full path for this run's screenshots
            storage_dir = os.path.join(base_storage_dir, run_dir_name)
            
            print(f"📁 Using screenshot directory: {storage_dir}")
            return StorageFactory.create_filesystem_storage(storage_dir, max_screenshots)
        else:
            # Default to memory storage
            persistence_file = config.get('persistence_file', 'screenshot_metadata.json')
            return StorageFactory.create_memory_storage(max_screenshots, persistence_file)
