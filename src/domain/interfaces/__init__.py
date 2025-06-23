"""
Domain Interfaces Package
Service interfaces for the screen agent domain
"""

from .screenshot_service import IScreenshotService
from .monitoring_service import IMonitoringService
from .analysis_service import IAnalysisService
from .storage_service import (
    IRepository,
    IFileStorageService, 
    IConfigurationService
)
from .event_service import (
    IEventService,
    INotificationService,
    EventHandler
)

__all__ = [
    # Core service interfaces
    "IScreenshotService",
    "IMonitoringService", 
    "IAnalysisService",
    
    # Storage interfaces
    "IRepository",
    "IFileStorageService",
    "IConfigurationService",
    
    # Event interfaces
    "IEventService",
    "INotificationService",
    "EventHandler"
]
