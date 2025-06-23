"""
Domain Repositories Package
Repository interfaces for data access abstraction
"""

from .screenshot_repository import IScreenshotRepository
from .configuration_repository import IConfigurationRepository
from .monitoring_repository import IMonitoringRepository

__all__ = [
    "IScreenshotRepository",
    "IConfigurationRepository", 
    "IMonitoringRepository"
]
