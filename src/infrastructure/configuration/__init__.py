"""
Configuration infrastructure for ScreenAgent
Provides validation, source management, and merging capabilities
"""

from .validators import (
    ConfigurationValidator,
    ValidationRule,
    ConfigurationType,
    ValidationError
)

from .sources import (
    IConfigurationSource,
    FileConfigurationSource,
    EnvironmentConfigurationSource,
    DefaultConfigurationSource,
    RuntimeConfigurationSource,
    ConfigurationSourceManager,
    SourceMetadata
)

from .mergers import (
    ConfigurationMerger,
    SmartConfigurationMerger,
    MergeStrategy,
    MergeRule,
    MergeResult
)

__all__ = [
    # Validation
    'ConfigurationValidator',
    'ValidationRule', 
    'ConfigurationType',
    'ValidationError',
    
    # Sources
    'IConfigurationSource',
    'FileConfigurationSource',
    'EnvironmentConfigurationSource', 
    'DefaultConfigurationSource',
    'RuntimeConfigurationSource',
    'ConfigurationSourceManager',
    'SourceMetadata',
    
    # Merging
    'ConfigurationMerger',
    'SmartConfigurationMerger',
    'MergeStrategy',
    'MergeRule',
    'MergeResult'
]
