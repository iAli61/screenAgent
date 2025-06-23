"""
Configuration Domain Exceptions
"""
from .base_exception import BaseScreenAgentException


class ConfigurationException(BaseScreenAgentException):
    """Base exception for configuration-related errors"""
    pass


class ConfigurationNotFoundError(ConfigurationException):
    """Exception for configuration not found"""
    
    def __init__(self, config_key: str, **kwargs):
        message = f"Configuration not found: {config_key}"
        super().__init__(message, error_code="CONFIG_NOT_FOUND", status_code=404, **kwargs)
        self.config_key = config_key


class ConfigurationValidationError(ConfigurationException):
    """Exception for configuration validation errors"""
    
    def __init__(self, message: str = "Invalid configuration", field: str = None, **kwargs):
        super().__init__(message, error_code="INVALID_CONFIG", status_code=400, **kwargs)
        self.field = field


class ConfigurationLoadError(ConfigurationException):
    """Exception for configuration loading errors"""
    
    def __init__(self, source: str, message: str = None, **kwargs):
        message = message or f"Failed to load configuration from {source}"
        super().__init__(message, error_code="CONFIG_LOAD_ERROR", status_code=500, **kwargs)
        self.source = source


class ConfigurationSaveError(ConfigurationException):
    """Exception for configuration saving errors"""
    
    def __init__(self, target: str, message: str = None, **kwargs):
        message = message or f"Failed to save configuration to {target}"
        super().__init__(message, error_code="CONFIG_SAVE_ERROR", status_code=500, **kwargs)
        self.target = target


class ConfigurationBackupError(ConfigurationException):
    """Exception for configuration backup errors"""
    
    def __init__(self, message: str = "Configuration backup error", **kwargs):
        super().__init__(message, error_code="BACKUP_ERROR", status_code=500, **kwargs)
