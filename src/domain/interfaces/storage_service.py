"""
Storage Service Interface
Defines the contract for data persistence and retrieval
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from pathlib import Path
from datetime import datetime

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    """Generic repository interface for CRUD operations"""
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """Update existing entity"""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: str) -> bool:
        """Delete entity by ID"""
        pass
    
    @abstractmethod
    async def list_all(
        self, 
        limit: Optional[int] = None, 
        offset: int = 0
    ) -> List[T]:
        """List all entities with pagination"""
        pass
    
    @abstractmethod
    async def find_by_criteria(self, criteria: Dict[str, Any]) -> List[T]:
        """Find entities matching criteria"""
        pass


class IFileStorageService(ABC):
    """Interface for file storage operations"""
    
    @abstractmethod
    async def save_file(
        self, 
        content: bytes, 
        filename: str,
        directory: Optional[Path] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Save file content to storage
        
        Args:
            content: File content as bytes
            filename: Name of the file
            directory: Optional directory path
            metadata: Optional file metadata
            
        Returns:
            Path where file was saved
        """
        pass
    
    @abstractmethod
    async def get_file(self, file_path: Path) -> Optional[bytes]:
        """
        Retrieve file content by path
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as bytes if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete_file(self, file_path: Path) -> bool:
        """
        Delete file by path
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_files(
        self, 
        directory: Path,
        pattern: Optional[str] = None,
        recursive: bool = False
    ) -> List[Path]:
        """
        List files in directory
        
        Args:
            directory: Directory to list files from
            pattern: Optional file pattern to match
            recursive: Whether to search recursively
            
        Returns:
            List of file paths
        """
        pass
    
    @abstractmethod
    async def get_file_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Get file information (size, modified date, etc.)
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        pass
    
    @abstractmethod
    async def cleanup_old_files(
        self, 
        directory: Path,
        max_age_days: int = 30,
        pattern: Optional[str] = None
    ) -> int:
        """
        Clean up old files in directory
        
        Args:
            directory: Directory to clean up
            max_age_days: Maximum age in days
            pattern: Optional file pattern to match
            
        Returns:
            Number of files deleted
        """
        pass


class IConfigurationService(ABC):
    """Interface for configuration management"""
    
    @abstractmethod
    async def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        pass
    
    @abstractmethod
    async def set_config(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        pass
    
    @abstractmethod
    async def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration values"""
        pass
    
    @abstractmethod
    async def reload_config(self) -> bool:
        """Reload configuration from source"""
        pass
    
    @abstractmethod
    async def validate_config(self) -> List[str]:
        """Validate configuration and return any errors"""
        pass
