"""
Storage Strategy Interface
Defines the contract for different storage backends
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from ...domain.entities.screenshot import Screenshot


class IStorageStrategy(ABC):
    """Interface for storage strategies"""
    
    @abstractmethod
    async def store(self, screenshot: Screenshot) -> bool:
        """Store a screenshot"""
        pass
    
    @abstractmethod
    async def retrieve(self, screenshot_id: str) -> Optional[Screenshot]:
        """Retrieve a screenshot by ID"""
        pass
    
    @abstractmethod
    async def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[Screenshot]:
        """List all screenshots with pagination"""
        pass
    
    @abstractmethod
    async def delete(self, screenshot_id: str) -> bool:
        """Delete a screenshot by ID"""
        pass
    
    @abstractmethod
    async def delete_all(self) -> bool:
        """Delete all screenshots"""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        pass
    
    @abstractmethod
    async def cleanup_old(self, max_age_hours: int) -> int:
        """Cleanup screenshots older than specified hours"""
        pass


class IStorageFactory(ABC):
    """Factory interface for creating storage strategies"""
    
    @abstractmethod
    def create_storage(self, storage_type: str, **kwargs) -> IStorageStrategy:
        """Create a storage strategy instance"""
        pass
