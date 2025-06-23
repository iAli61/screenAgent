"""
Storage Factory Implementation
Creates storage strategy instances based on configuration
"""
from typing import Dict, Any

from .storage_strategy import IStorageFactory, IStorageStrategy
from .file_storage_strategy import FileStorageStrategy
from .memory_storage_strategy import MemoryStorageStrategy


class StorageFactory(IStorageFactory):
    """Factory for creating storage strategies"""
    
    def create_storage(self, storage_type: str, **kwargs) -> IStorageStrategy:
        """Create a storage strategy instance"""
        
        if storage_type.lower() == 'file':
            return FileStorageStrategy(
                base_path=kwargs.get('base_path', 'screenshots'),
                max_screenshots=kwargs.get('max_screenshots', 1000)
            )
        
        elif storage_type.lower() == 'memory':
            return MemoryStorageStrategy(
                max_screenshots=kwargs.get('max_screenshots', 100),
                persistence_file=kwargs.get('persistence_file')
            )
        
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")


class StorageManager:
    """Simplified storage manager using strategy pattern"""
    
    def __init__(self, storage_strategy: IStorageStrategy):
        self._strategy = storage_strategy
    
    @property
    def strategy(self) -> IStorageStrategy:
        """Get the current storage strategy"""
        return self._strategy
    
    def set_strategy(self, strategy: IStorageStrategy):
        """Set a new storage strategy"""
        self._strategy = strategy
    
    # Delegate all operations to the strategy
    async def store_screenshot(self, screenshot) -> bool:
        """Store a screenshot"""
        return await self._strategy.store(screenshot)
    
    async def retrieve_screenshot(self, screenshot_id: str):
        """Retrieve a screenshot by ID"""
        return await self._strategy.retrieve(screenshot_id)
    
    async def list_screenshots(self, limit=None, offset=0):
        """List screenshots with pagination"""
        return await self._strategy.list_all(limit, offset)
    
    async def delete_screenshot(self, screenshot_id: str) -> bool:
        """Delete a screenshot by ID"""
        return await self._strategy.delete(screenshot_id)
    
    async def delete_all_screenshots(self) -> bool:
        """Delete all screenshots"""
        return await self._strategy.delete_all()
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        return await self._strategy.get_stats()
    
    async def cleanup_old_screenshots(self, max_age_hours: int) -> int:
        """Cleanup old screenshots"""
        return await self._strategy.cleanup_old(max_age_hours)
