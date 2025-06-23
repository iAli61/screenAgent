"""
Configuration sources for ScreenAgent
Handles loading configuration from multiple sources with priority hierarchy
"""
import os
import json
from typing import Dict, Any, Optional, Protocol, List
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


class IConfigurationSource(Protocol):
    """Interface for configuration sources"""
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from this source"""
        ...
    
    def save(self, config: Dict[str, Any]) -> bool:
        """Save configuration to this source (if writable)"""
        ...
    
    def is_writable(self) -> bool:
        """Check if this source supports writing"""
        ...
    
    def get_priority(self) -> int:
        """Get priority level (higher = more important)"""
        ...
    
    def get_name(self) -> str:
        """Get source name for debugging"""
        ...


@dataclass
class SourceMetadata:
    """Metadata about a configuration source"""
    name: str
    priority: int
    writable: bool
    available: bool
    path: Optional[str] = None
    error: Optional[str] = None


class FileConfigurationSource:
    """Configuration source that reads from JSON files"""
    
    def __init__(self, file_path: str, priority: int = 1, writable: bool = True):
        self.file_path = Path(file_path)
        self.priority = priority
        self.writable = writable
        self._name = f"file:{file_path}"
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if not self.file_path.exists():
                return {}
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError, OSError) as e:
            print(f"Warning: Could not load config from {self.file_path}: {e}")
            return {}
    
    def save(self, config: Dict[str, Any]) -> bool:
        """Save configuration to JSON file"""
        if not self.writable:
            return False
        
        try:
            # Ensure directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, sort_keys=True)
            return True
        except (IOError, OSError) as e:
            print(f"Error saving config to {self.file_path}: {e}")
            return False
    
    def is_writable(self) -> bool:
        """Check if file source is writable"""
        return self.writable
    
    def get_priority(self) -> int:
        """Get source priority"""
        return self.priority
    
    def get_name(self) -> str:
        """Get source name"""
        return self._name
    
    def exists(self) -> bool:
        """Check if file exists"""
        return self.file_path.exists()
    
    def get_metadata(self) -> SourceMetadata:
        """Get source metadata"""
        error = None
        available = True
        
        try:
            # Test if we can read the file
            if self.file_path.exists():
                with open(self.file_path, 'r') as f:
                    json.load(f)
        except Exception as e:
            error = str(e)
            available = False
        
        return SourceMetadata(
            name=self._name,
            priority=self.priority,
            writable=self.writable,
            available=available,
            path=str(self.file_path),
            error=error
        )


class EnvironmentConfigurationSource:
    """Configuration source that reads from environment variables"""
    
    def __init__(self, prefix: str = "SCREENAGENT_", priority: int = 3):
        self.prefix = prefix.upper()
        self.priority = priority
        self._name = f"env:{prefix}"
        
        # Mapping of environment variable names to config keys
        self._env_mapping = {
            f"{self.prefix}ROI": "roi",
            f"{self.prefix}PORT": "port",
            f"{self.prefix}CHANGE_THRESHOLD": "change_threshold",
            f"{self.prefix}CHECK_INTERVAL": "check_interval",
            f"{self.prefix}LLM_ENABLED": "llm_enabled",
            f"{self.prefix}LLM_MODEL": "llm_model",
            f"{self.prefix}LLM_PROMPT": "llm_prompt",
            f"{self.prefix}KEYBOARD_SHORTCUT": "keyboard_shortcut",
            f"{self.prefix}MAX_SCREENSHOTS": "max_screenshots",
            f"{self.prefix}AUTO_CLEANUP": "auto_cleanup",
            f"{self.prefix}STORAGE_TYPE": "storage_type",
            f"{self.prefix}SCREENSHOT_DIR": "screenshot_dir",
            f"{self.prefix}TEMP_SCREENSHOT_PATH": "temp_screenshot_path",
            f"{self.prefix}AUTO_START_MONITORING": "auto_start_monitoring",
            f"{self.prefix}SCREENSHOT_FORMAT": "screenshot_format",
            f"{self.prefix}JPEG_QUALITY": "jpeg_quality",
            f"{self.prefix}DEFAULT_STRATEGY": "default_strategy",
            
            # Common external env vars
            "OPENAI_API_KEY": "openai_api_key",
            "AZURE_AI_ENDPOINT": "azure_ai_endpoint",
            "AZURE_AI_KEY": "azure_ai_key",
            "LLM_ENABLED": "llm_enabled",
            "LLM_MODEL": "llm_model",
            "LLM_PROMPT": "llm_prompt"
        }
    
    def load(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {}
        
        for env_key, config_key in self._env_mapping.items():
            value = os.getenv(env_key)
            if value is not None:
                # Parse value based on expected type
                parsed_value = self._parse_env_value(config_key, value)
                if parsed_value is not None:
                    config[config_key] = parsed_value
        
        return config
    
    def save(self, config: Dict[str, Any]) -> bool:
        """Environment variables are not writable from application"""
        return False
    
    def is_writable(self) -> bool:
        """Environment source is read-only"""
        return False
    
    def get_priority(self) -> int:
        """Get source priority"""
        return self.priority
    
    def get_name(self) -> str:
        """Get source name"""
        return self._name
    
    def get_metadata(self) -> SourceMetadata:
        """Get source metadata"""
        # Count available environment variables
        available_vars = [env_key for env_key in self._env_mapping.keys() if os.getenv(env_key) is not None]
        
        return SourceMetadata(
            name=self._name,
            priority=self.priority,
            writable=False,
            available=len(available_vars) > 0,
            path=f"Environment variables: {len(available_vars)} found"
        )
    
    def _parse_env_value(self, config_key: str, value: str) -> Any:
        """Parse environment variable value to appropriate type"""
        try:
            # Boolean values
            if config_key in ['llm_enabled', 'auto_cleanup', 'auto_start_monitoring']:
                return value.lower() in ('true', '1', 'yes', 'on')
            
            # Integer values
            elif config_key in ['port', 'max_screenshots', 'jpeg_quality']:
                return int(value)
            
            # Float values
            elif config_key in ['change_threshold', 'check_interval']:
                return float(value)
            
            # ROI tuple
            elif config_key == 'roi':
                # Parse comma-separated values: "100,100,800,800"
                parts = [int(x.strip()) for x in value.split(',')]
                if len(parts) == 4:
                    return parts
                return None
            
            # String values (default)
            else:
                return value
                
        except (ValueError, TypeError):
            print(f"Warning: Could not parse environment variable {config_key}={value}")
            return None


class DefaultConfigurationSource:
    """Configuration source that provides default values"""
    
    def __init__(self, priority: int = 0):
        self.priority = priority
        self._name = "defaults"
    
    def load(self) -> Dict[str, Any]:
        """Load default configuration values"""
        # Import here to avoid circular imports
        from .validators import ConfigurationValidator
        
        validator = ConfigurationValidator()
        return validator.get_all_defaults()
    
    def save(self, config: Dict[str, Any]) -> bool:
        """Defaults are not writable"""
        return False
    
    def is_writable(self) -> bool:
        """Defaults source is read-only"""
        return False
    
    def get_priority(self) -> int:
        """Get source priority"""
        return self.priority
    
    def get_name(self) -> str:
        """Get source name"""
        return self._name
    
    def get_metadata(self) -> SourceMetadata:
        """Get source metadata"""
        return SourceMetadata(
            name=self._name,
            priority=self.priority,
            writable=False,
            available=True,
            path="Built-in defaults"
        )


class RuntimeConfigurationSource:
    """Configuration source for runtime changes (highest priority)"""
    
    def __init__(self, priority: int = 10):
        self.priority = priority
        self._name = "runtime"
        self._runtime_config: Dict[str, Any] = {}
    
    def load(self) -> Dict[str, Any]:
        """Load runtime configuration"""
        return self._runtime_config.copy()
    
    def save(self, config: Dict[str, Any]) -> bool:
        """Save to runtime configuration"""
        self._runtime_config.update(config)
        return True
    
    def set_value(self, key: str, value: Any) -> bool:
        """Set a single runtime value"""
        self._runtime_config[key] = value
        return True
    
    def clear(self):
        """Clear all runtime configuration"""
        self._runtime_config.clear()
    
    def is_writable(self) -> bool:
        """Runtime source is writable"""
        return True
    
    def get_priority(self) -> int:
        """Get source priority"""
        return self.priority
    
    def get_name(self) -> str:
        """Get source name"""
        return self._name
    
    def get_metadata(self) -> SourceMetadata:
        """Get source metadata"""
        return SourceMetadata(
            name=self._name,
            priority=self.priority,
            writable=True,
            available=True,
            path=f"Runtime values: {len(self._runtime_config)} set"
        )


class ConfigurationSourceManager:
    """Manages multiple configuration sources with priority ordering"""
    
    def __init__(self):
        self._sources: List[IConfigurationSource] = []
    
    def add_source(self, source: IConfigurationSource):
        """Add a configuration source"""
        self._sources.append(source)
        # Sort by priority (highest first)
        self._sources.sort(key=lambda s: s.get_priority(), reverse=True)
    
    def remove_source(self, source_name: str):
        """Remove a configuration source by name"""
        self._sources = [s for s in self._sources if s.get_name() != source_name]
    
    def get_merged_config(self) -> Dict[str, Any]:
        """Get configuration merged from all sources (priority order)"""
        merged = {}
        
        # Start with lowest priority and work up
        for source in reversed(self._sources):
            try:
                source_config = source.load()
                merged.update(source_config)
            except Exception as e:
                print(f"Warning: Error loading from source {source.get_name()}: {e}")
        
        return merged
    
    def save_to_writable_sources(self, config: Dict[str, Any]) -> bool:
        """Save configuration to all writable sources"""
        success = False
        
        for source in self._sources:
            if source.is_writable():
                try:
                    if source.save(config):
                        success = True
                except Exception as e:
                    print(f"Warning: Error saving to source {source.get_name()}: {e}")
        
        return success
    
    def get_source_metadata(self) -> List[SourceMetadata]:
        """Get metadata for all sources"""
        metadata = []
        
        for source in self._sources:
            try:
                if hasattr(source, 'get_metadata'):
                    metadata.append(source.get_metadata())
                else:
                    # Fallback metadata
                    metadata.append(SourceMetadata(
                        name=source.get_name(),
                        priority=source.get_priority(),
                        writable=source.is_writable(),
                        available=True
                    ))
            except Exception as e:
                metadata.append(SourceMetadata(
                    name=source.get_name(),
                    priority=source.get_priority(),
                    writable=False,
                    available=False,
                    error=str(e)
                ))
        
        return metadata
    
    def get_source_by_name(self, name: str) -> Optional[IConfigurationSource]:
        """Get source by name"""
        for source in self._sources:
            if source.get_name() == name:
                return source
        return None
    
    def get_sources(self) -> List[IConfigurationSource]:
        """Get all sources"""
        return self._sources.copy()
