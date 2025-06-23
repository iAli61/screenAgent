"""
Configuration Repository Interface
Abstract data access for configuration management
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime


class IConfigurationRepository(ABC):
    """Interface for configuration data access operations"""
    
    @abstractmethod
    async def get_config(self, key: str) -> Optional[Any]:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (supports dot notation for nested values)
            
        Returns:
            Configuration value if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def set_config(self, key: str, value: Any) -> bool:
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Returns:
            True if set successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def delete_config(self, key: str) -> bool:
        """
        Delete configuration key
        
        Args:
            key: Configuration key to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_all_config(self) -> Dict[str, Any]:
        """
        Get all configuration values
        
        Returns:
            Dictionary with all configuration key-value pairs
        """
        pass
    
    @abstractmethod
    async def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get configuration section
        
        Args:
            section: Section name
            
        Returns:
            Dictionary with section configuration
        """
        pass
    
    @abstractmethod
    async def update_section(self, section: str, config: Dict[str, Any]) -> bool:
        """
        Update entire configuration section
        
        Args:
            section: Section name
            config: Section configuration
            
        Returns:
            True if updated successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def has_key(self, key: str) -> bool:
        """
        Check if configuration key exists
        
        Args:
            key: Configuration key
            
        Returns:
            True if key exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all configuration keys, optionally filtered by pattern
        
        Args:
            pattern: Optional pattern to filter keys
            
        Returns:
            List of configuration keys
        """
        pass
    
    @abstractmethod
    async def backup_config(self) -> str:
        """
        Create backup of current configuration
        
        Returns:
            Backup identifier or filename
        """
        pass
    
    @abstractmethod
    async def restore_config(self, backup_id: str) -> bool:
        """
        Restore configuration from backup
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            True if restored successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_config_history(self, key: str) -> List[Dict[str, Any]]:
        """
        Get configuration change history for a key
        
        Args:
            key: Configuration key
            
        Returns:
            List of configuration changes with timestamps
        """
        pass
    
    @abstractmethod
    async def validate_config(self) -> List[str]:
        """
        Validate current configuration
        
        Returns:
            List of validation errors, empty if valid
        """
        pass
    
    @abstractmethod
    async def get_schema(self) -> Dict[str, Any]:
        """
        Get configuration schema
        
        Returns:
            Configuration schema definition
        """
        pass
    
    @abstractmethod
    async def reload_from_source(self) -> bool:
        """
        Reload configuration from source
        
        Returns:
            True if reloaded successfully, False otherwise
        """
        pass
