"""
Configuration validation for ScreenAgent
Provides type safety and constraint validation for configuration values
"""
from typing import Any, Dict, List, Tuple, Union, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import os
import re


class ValidationError(Exception):
    """Raised when configuration validation fails"""
    pass


class ConfigurationType(Enum):
    """Types of configuration values"""
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    STRING = "string"
    PATH = "path"
    ROI = "roi"
    PORT = "port"
    ENUM = "enum"
    LIST = "list"


@dataclass
class ValidationRule:
    """Configuration validation rule"""
    key: str
    config_type: ConfigurationType
    required: bool = False
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    allowed_values: Optional[List[Any]] = None
    pattern: Optional[str] = None
    custom_validator: Optional[Callable[[Any], bool]] = None
    description: str = ""
    default_value: Any = None


class ConfigurationValidator:
    """Validates configuration values according to defined rules"""
    
    def __init__(self):
        self._rules: Dict[str, ValidationRule] = {}
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize default validation rules"""
        rules = [
            ValidationRule(
                key="roi",
                config_type=ConfigurationType.ROI,
                required=True,
                description="Region of interest coordinates (x, y, width, height)",
                default_value=(100, 100, 800, 800),
                custom_validator=self._validate_roi
            ),
            ValidationRule(
                key="port",
                config_type=ConfigurationType.PORT,
                required=True,
                min_value=1024,
                max_value=65535,
                description="HTTP server port",
                default_value=8000
            ),
            ValidationRule(
                key="max_port_attempts",
                config_type=ConfigurationType.INTEGER,
                min_value=1,
                max_value=50,
                description="Maximum port search attempts",
                default_value=10
            ),
            ValidationRule(
                key="change_threshold",
                config_type=ConfigurationType.FLOAT,
                min_value=0.0,
                max_value=100.0,
                description="Change detection threshold percentage",
                default_value=20.0
            ),
            ValidationRule(
                key="check_interval",
                config_type=ConfigurationType.FLOAT,
                min_value=0.1,
                max_value=60.0,
                description="Check interval in seconds",
                default_value=0.5
            ),
            ValidationRule(
                key="llm_enabled",
                config_type=ConfigurationType.BOOLEAN,
                description="Enable LLM analysis",
                default_value=False
            ),
            ValidationRule(
                key="llm_model",
                config_type=ConfigurationType.STRING,
                allowed_values=["gpt-4o", "gpt-4-vision-preview", "gpt-3.5-turbo", "claude-3-opus"],
                description="LLM model to use",
                default_value="gpt-4o"
            ),
            ValidationRule(
                key="llm_prompt",
                config_type=ConfigurationType.STRING,
                min_value=10,  # minimum length
                max_value=1000,  # maximum length
                description="LLM analysis prompt",
                default_value="Describe what you see in this screenshot, focusing on the most important elements."
            ),
            ValidationRule(
                key="keyboard_shortcut",
                config_type=ConfigurationType.STRING,
                pattern=r"^(ctrl\+)?(shift\+)?(alt\+)?[a-z0-9]+$|^f[1-9]|f1[0-2]$",
                description="Keyboard shortcut for screenshots",
                default_value="f12"
            ),
            ValidationRule(
                key="max_screenshots",
                config_type=ConfigurationType.INTEGER,
                min_value=1,
                max_value=10000,
                description="Maximum screenshots to store",
                default_value=100
            ),
            ValidationRule(
                key="auto_cleanup",
                config_type=ConfigurationType.BOOLEAN,
                description="Automatically cleanup old screenshots",
                default_value=True
            ),
            ValidationRule(
                key="storage_type",
                config_type=ConfigurationType.ENUM,
                allowed_values=["filesystem", "memory"],
                description="Storage backend type",
                default_value="filesystem"
            ),
            ValidationRule(
                key="screenshot_dir",
                config_type=ConfigurationType.PATH,
                description="Screenshot storage directory",
                default_value="screenshots",
                custom_validator=self._validate_directory_path
            ),
            ValidationRule(
                key="temp_screenshot_path",
                config_type=ConfigurationType.PATH,
                description="Temporary screenshot file path",
                default_value="temp/temp_screenshot.png",
                custom_validator=self._validate_file_path
            ),
            ValidationRule(
                key="auto_start_monitoring",
                config_type=ConfigurationType.BOOLEAN,
                description="Automatically start monitoring on launch",
                default_value=False
            ),
            ValidationRule(
                key="screenshot_format",
                config_type=ConfigurationType.ENUM,
                allowed_values=["PNG", "JPEG", "WEBP"],
                description="Screenshot image format",
                default_value="PNG"
            ),
            ValidationRule(
                key="jpeg_quality",
                config_type=ConfigurationType.INTEGER,
                min_value=1,
                max_value=100,
                description="JPEG compression quality",
                default_value=95
            ),
            ValidationRule(
                key="default_strategy",
                config_type=ConfigurationType.ENUM,
                allowed_values=["threshold", "pixel_diff", "hash_comparison"],
                description="Default change detection strategy",
                default_value="threshold"
            )
        ]
        
        for rule in rules:
            self._rules[rule.key] = rule
    
    def validate_value(self, key: str, value: Any) -> Tuple[bool, str]:
        """
        Validate a single configuration value
        
        Args:
            key: Configuration key
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if key not in self._rules:
            return False, f"Unknown configuration key: {key}"
        
        rule = self._rules[key]
        
        try:
            # Type validation
            validated_value = self._validate_type(value, rule)
            
            # Range validation
            if rule.min_value is not None or rule.max_value is not None:
                if not self._validate_range(validated_value, rule):
                    return False, f"{key}: Value {validated_value} out of range [{rule.min_value}, {rule.max_value}]"
            
            # Allowed values validation
            if rule.allowed_values is not None:
                if validated_value not in rule.allowed_values:
                    return False, f"{key}: Value {validated_value} not in allowed values {rule.allowed_values}"
            
            # Pattern validation
            if rule.pattern is not None:
                if not re.match(rule.pattern, str(validated_value)):
                    return False, f"{key}: Value {validated_value} does not match required pattern"
            
            # Custom validation
            if rule.custom_validator is not None:
                if not rule.custom_validator(validated_value):
                    return False, f"{key}: Custom validation failed for value {validated_value}"
            
            return True, ""
            
        except Exception as e:
            return False, f"{key}: Validation error - {str(e)}"
    
    def validate_config(self, config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate entire configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required keys
        for key, rule in self._rules.items():
            if rule.required and key not in config:
                errors.append(f"Required configuration key missing: {key}")
        
        # Validate present keys
        for key, value in config.items():
            is_valid, error_msg = self.validate_value(key, value)
            if not is_valid:
                errors.append(error_msg)
        
        return len(errors) == 0, errors
    
    def get_default_value(self, key: str) -> Any:
        """Get default value for a configuration key"""
        if key in self._rules:
            return self._rules[key].default_value
        return None
    
    def get_all_defaults(self) -> Dict[str, Any]:
        """Get all default configuration values"""
        return {key: rule.default_value for key, rule in self._rules.items() if rule.default_value is not None}
    
    def get_rule(self, key: str) -> Optional[ValidationRule]:
        """Get validation rule for a key"""
        return self._rules.get(key)
    
    def get_all_rules(self) -> Dict[str, ValidationRule]:
        """Get all validation rules"""
        return self._rules.copy()
    
    def _validate_type(self, value: Any, rule: ValidationRule) -> Any:
        """Validate and convert value to correct type"""
        config_type = rule.config_type
        
        if config_type == ConfigurationType.INTEGER:
            return int(value)
        elif config_type == ConfigurationType.FLOAT:
            return float(value)
        elif config_type == ConfigurationType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            return bool(value)
        elif config_type == ConfigurationType.STRING:
            return str(value)
        elif config_type == ConfigurationType.PATH:
            return str(value)
        elif config_type == ConfigurationType.PORT:
            port = int(value)
            if not (1 <= port <= 65535):
                raise ValueError(f"Port {port} out of valid range")
            return port
        elif config_type == ConfigurationType.ROI:
            if isinstance(value, (list, tuple)) and len(value) == 4:
                return tuple(int(x) for x in value)
            raise ValueError("ROI must be a 4-element tuple/list")
        elif config_type == ConfigurationType.ENUM:
            return value  # Enum validation handled by allowed_values
        elif config_type == ConfigurationType.LIST:
            if not isinstance(value, list):
                raise ValueError("Expected list value")
            return value
        else:
            return value
    
    def _validate_range(self, value: Any, rule: ValidationRule) -> bool:
        """Validate numeric ranges"""
        try:
            if rule.config_type == ConfigurationType.STRING:
                # For strings, min/max refers to length
                length = len(str(value))
                if rule.min_value is not None and length < rule.min_value:
                    return False
                if rule.max_value is not None and length > rule.max_value:
                    return False
            else:
                # For numeric values
                if rule.min_value is not None and value < rule.min_value:
                    return False
                if rule.max_value is not None and value > rule.max_value:
                    return False
            return True
        except Exception:
            return False
    
    def _validate_roi(self, roi: Tuple[int, int, int, int]) -> bool:
        """Custom validation for ROI coordinates"""
        x, y, width, height = roi
        
        # All values should be positive
        if any(val < 0 for val in roi):
            return False
        
        # Width and height should be reasonable
        if width < 10 or height < 10:
            return False
        
        # Coordinates should be reasonable (not exceeding common screen sizes)
        if x > 10000 or y > 10000 or width > 10000 or height > 10000:
            return False
        
        return True
    
    def _validate_directory_path(self, path: str) -> bool:
        """Custom validation for directory paths"""
        try:
            # Check if path is valid
            if not path or path.strip() == "":
                return False
            
            # Check for invalid characters
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
            if any(char in path for char in invalid_chars):
                return False
            
            # Try to create the directory if it doesn't exist
            os.makedirs(path, exist_ok=True)
            return True
        except Exception:
            return False
    
    def _validate_file_path(self, path: str) -> bool:
        """Custom validation for file paths"""
        try:
            # Check if path is valid
            if not path or path.strip() == "":
                return False
            
            # Check for invalid characters
            invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
            if any(char in path for char in invalid_chars):
                return False
            
            # Check directory part
            directory = os.path.dirname(path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            return True
        except Exception:
            return False
