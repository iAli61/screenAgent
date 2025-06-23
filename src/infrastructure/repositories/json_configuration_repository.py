"""
JSON Configuration Repository Implementation
Stores configuration in JSON files with validation and backup
"""
import json
import asyncio
import shutil
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path
import logging

from src.domain.repositories.configuration_repository import IConfigurationRepository


logger = logging.getLogger(__name__)


class JsonConfigurationRepository(IConfigurationRepository):
    """JSON file-based implementation of configuration repository"""
    
    def __init__(self, config_file_path: Path):
        self.config_file_path = Path(config_file_path)
        self.backup_directory = self.config_file_path.parent / "backups"
        
        # Ensure directories exist
        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_directory.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self._config: Dict[str, Any] = {}
        self._config_loaded = False
        self._lock = asyncio.Lock()
        
        # Default configuration schema
        self._schema = {
            "screenshot": {
                "default_format": "PNG",
                "quality": 95,
                "compression": "fast"
            },
            "monitoring": {
                "default_threshold": 20.0,
                "default_interval": 0.5,
                "max_sessions": 10
            },
            "storage": {
                "max_age_days": 30,
                "max_size_mb": 1000,
                "cleanup_interval_hours": 24
            },
            "server": {
                "host": "localhost",
                "port": 8000,
                "max_port_attempts": 10,
                "debug": False
            }
        }
    
    async def _ensure_config_loaded(self):
        """Ensure configuration is loaded from file"""
        if not self._config_loaded:
            await self._load_config()
    
    async def _load_config(self):
        """Load configuration from file"""
        async with self._lock:
            try:
                if self.config_file_path.exists():
                    with open(self.config_file_path, 'r') as f:
                        self._config = json.load(f)
                else:
                    # Create default configuration
                    self._config = self._schema.copy()
                    await self._save_config()
                
                self._config_loaded = True
                logger.info(f"Loaded configuration from {self.config_file_path}")
                
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                self._config = self._schema.copy()
                self._config_loaded = True
    
    async def _save_config(self):
        """Save configuration to file"""
        try:
            # Create backup before saving
            await self._create_backup()
            
            with open(self.config_file_path, 'w') as f:
                json.dump(self._config, f, indent=2, default=str)
            
            logger.debug(f"Saved configuration to {self.config_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise
    
    async def _create_backup(self) -> str:
        """Create backup of current configuration"""
        try:
            if not self.config_file_path.exists():
                return ""
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"config_backup_{timestamp}.json"
            backup_path = self.backup_directory / backup_filename
            
            shutil.copy2(self.config_file_path, backup_path)
            
            logger.debug(f"Created configuration backup: {backup_filename}")
            return backup_filename
            
        except Exception as e:
            logger.error(f"Failed to create configuration backup: {e}")
            return ""
    
    def _get_nested_value(self, config: Dict[str, Any], key: str) -> Any:
        """Get nested configuration value using dot notation"""
        keys = key.split('.')
        value = config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def _set_nested_value(self, config: Dict[str, Any], key: str, value: Any):
        """Set nested configuration value using dot notation"""
        keys = key.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the final value
        current[keys[-1]] = value
    
    async def get_config(self, key: str) -> Optional[Any]:
        """Get configuration value by key"""
        await self._ensure_config_loaded()
        
        async with self._lock:
            return self._get_nested_value(self._config, key)
    
    async def set_config(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        await self._ensure_config_loaded()
        
        async with self._lock:
            try:
                self._set_nested_value(self._config, key, value)
                await self._save_config()
                
                logger.info(f"Set configuration {key} = {value}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to set configuration {key}: {e}")
                return False
    
    async def delete_config(self, key: str) -> bool:
        """Delete configuration key"""
        await self._ensure_config_loaded()
        
        async with self._lock:
            try:
                keys = key.split('.')
                current = self._config
                
                # Navigate to the parent of the target key
                for k in keys[:-1]:
                    if k not in current:
                        return False
                    current = current[k]
                
                # Delete the final key
                if keys[-1] in current:
                    del current[keys[-1]]
                    await self._save_config()
                    
                    logger.info(f"Deleted configuration key: {key}")
                    return True
                
                return False
                
            except Exception as e:
                logger.error(f"Failed to delete configuration {key}: {e}")
                return False
    
    async def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration values"""
        await self._ensure_config_loaded()
        
        async with self._lock:
            return self._config.copy()
    
    async def get_section(self, section: str) -> Dict[str, Any]:
        """Get configuration section"""
        await self._ensure_config_loaded()
        
        async with self._lock:
            return self._config.get(section, {}).copy()
    
    async def update_section(self, section: str, config: Dict[str, Any]) -> bool:
        """Update entire configuration section"""
        await self._ensure_config_loaded()
        
        async with self._lock:
            try:
                self._config[section] = config
                await self._save_config()
                
                logger.info(f"Updated configuration section: {section}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to update section {section}: {e}")
                return False
    
    async def has_key(self, key: str) -> bool:
        """Check if configuration key exists"""
        await self._ensure_config_loaded()
        
        async with self._lock:
            return self._get_nested_value(self._config, key) is not None
    
    async def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all configuration keys, optionally filtered by pattern"""
        await self._ensure_config_loaded()
        
        def _get_all_keys(config: Dict[str, Any], prefix: str = "") -> List[str]:
            keys = []
            for key, value in config.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.append(full_key)
                
                if isinstance(value, dict):
                    keys.extend(_get_all_keys(value, full_key))
            
            return keys
        
        async with self._lock:
            all_keys = _get_all_keys(self._config)
            
            if pattern:
                # Simple pattern matching (contains)
                return [key for key in all_keys if pattern in key]
            
            return all_keys
    
    async def backup_config(self) -> str:
        """Create backup of current configuration"""
        await self._ensure_config_loaded()
        return await self._create_backup()
    
    async def restore_config(self, backup_id: str) -> bool:
        """Restore configuration from backup"""
        try:
            backup_path = self.backup_directory / backup_id
            
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_id}")
                return False
            
            # Load backup configuration
            with open(backup_path, 'r') as f:
                backup_config = json.load(f)
            
            async with self._lock:
                self._config = backup_config
                await self._save_config()
            
            logger.info(f"Restored configuration from backup: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore configuration from {backup_id}: {e}")
            return False
    
    async def get_config_history(self, key: str) -> List[Dict[str, Any]]:
        """Get configuration change history for a key"""
        # TODO: Implement configuration history tracking
        # For now, return empty list
        return []
    
    async def validate_config(self) -> List[str]:
        """Validate current configuration"""
        await self._ensure_config_loaded()
        
        errors = []
        
        # Basic validation against schema
        for section, section_config in self._schema.items():
            if section not in self._config:
                errors.append(f"Missing configuration section: {section}")
                continue
            
            for key, default_value in section_config.items():
                if key not in self._config[section]:
                    errors.append(f"Missing configuration key: {section}.{key}")
                else:
                    # Type validation
                    actual_value = self._config[section][key]
                    if type(actual_value) != type(default_value):
                        errors.append(
                            f"Invalid type for {section}.{key}: "
                            f"expected {type(default_value).__name__}, "
                            f"got {type(actual_value).__name__}"
                        )
        
        return errors
    
    async def get_schema(self) -> Dict[str, Any]:
        """Get configuration schema"""
        return self._schema.copy()
    
    async def reload_from_source(self) -> bool:
        """Reload configuration from source"""
        try:
            async with self._lock:
                self._config_loaded = False
            
            await self._load_config()
            logger.info("Reloaded configuration from source")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            return False
