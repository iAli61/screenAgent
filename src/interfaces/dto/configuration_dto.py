"""
Configuration-related Data Transfer Objects
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class ConfigurationRequest:
    """Request to get configuration"""
    pass


@dataclass
class ConfigurationResponse:
    """Response containing configuration"""
    success: bool
    configuration: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class ConfigurationUpdateRequest:
    """Request to update configuration"""
    configuration: Dict[str, Any]


@dataclass
class ConfigurationUpdateResponse:
    """Response after updating configuration"""
    success: bool
    message: Optional[str] = None
    updated_fields: Optional[List[str]] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ConfigurationResetRequest:
    """Request to reset configuration"""
    section: Optional[str] = None


@dataclass
class ConfigurationResetResponse:
    """Response after resetting configuration"""
    success: bool
    message: Optional[str] = None
    reset_section: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ConfigurationValidationRequest:
    """Request to validate configuration"""
    configuration: Dict[str, Any]


@dataclass
class ConfigurationValidationResponse:
    """Response containing validation results"""
    success: bool
    validation: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class ConfigurationSchemaResponse:
    """Response containing configuration schema"""
    success: bool
    schema: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
