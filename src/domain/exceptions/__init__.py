"""
Domain Exceptions Package
Exports all domain exceptions for the ScreenAgent application
"""

from .base_exception import (
    BaseScreenAgentException,
    DomainValidationError,
    DomainNotFoundError,
    DomainConflictError,
    DomainPermissionError,
    DomainConfigurationError
)

from .screenshot_exceptions import (
    ScreenshotException,
    ScreenshotCaptureError,
    ScreenshotNotFoundError,
    ScreenshotStorageError,
    ScreenshotFormatError,
    ScreenshotPermissionError
)

from .monitoring_exceptions import (
    MonitoringException,
    MonitoringSessionNotFoundError,
    MonitoringSessionConflictError,
    MonitoringConfigurationError,
    MonitoringCapacityError,
    MonitoringResourceError
)

from .configuration_exceptions import (
    ConfigurationException,
    ConfigurationNotFoundError,
    ConfigurationValidationError,
    ConfigurationLoadError,
    ConfigurationSaveError,
    ConfigurationBackupError
)

__all__ = [
    # Base exceptions
    "BaseScreenAgentException",
    "DomainValidationError", 
    "DomainNotFoundError",
    "DomainConflictError",
    "DomainPermissionError",
    "DomainConfigurationError",
    
    # Screenshot exceptions
    "ScreenshotException",
    "ScreenshotCaptureError",
    "ScreenshotNotFoundError",
    "ScreenshotStorageError",
    "ScreenshotFormatError",
    "ScreenshotPermissionError",
    
    # Monitoring exceptions
    "MonitoringException",
    "MonitoringSessionNotFoundError",
    "MonitoringSessionConflictError",
    "MonitoringConfigurationError",
    "MonitoringCapacityError",
    "MonitoringResourceError",
    
    # Configuration exceptions
    "ConfigurationException",
    "ConfigurationNotFoundError",
    "ConfigurationValidationError",
    "ConfigurationLoadError",
    "ConfigurationSaveError",
    "ConfigurationBackupError"
]
