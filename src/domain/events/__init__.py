"""
Domain Events Package
Events for the screen agent domain
"""

from .screenshot_captured import (
    BaseDomainEvent,
    ScreenshotCaptured,
    ScreenshotAnalysisCompleted as AnalysisCompleted,
    ScreenshotAnalysisFailed as AnalysisFailed
)

from .monitoring_started import (
    MonitoringStarted,
    MonitoringStopped,
    MonitoringPaused,
    MonitoringResumed,
    ChangeDetected,
    ROIUpdated,
    MonitoringError
)

from .system_events import (
    SystemStarted,
    SystemShutdown,
    ConfigurationChanged,
    StorageCleanup,
    HealthCheckPerformed,
    ResourceLimit,
    ServiceError
)

__all__ = [
    # Base event
    "BaseDomainEvent",
    
    # Screenshot events
    "ScreenshotCaptured", 
    "AnalysisCompleted",
    "AnalysisFailed",
    
    # Monitoring events
    "MonitoringStarted",
    "MonitoringStopped", 
    "MonitoringPaused",
    "MonitoringResumed",
    "ChangeDetected",
    "ROIUpdated",
    "MonitoringError",
    
    # System events
    "SystemStarted",
    "SystemShutdown",
    "ConfigurationChanged",
    "StorageCleanup",
    "HealthCheckPerformed",
    "ResourceLimit",
    "ServiceError"
]
