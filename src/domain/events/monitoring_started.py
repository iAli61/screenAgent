"""
Monitoring domain events
Events related to ROI monitoring activities
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid
from .screenshot_captured import BaseDomainEvent


@dataclass
class MonitoringStarted(BaseDomainEvent):
    """Event fired when ROI monitoring starts"""
    
    session_id: str = ""
    roi_id: str = ""
    roi_coordinates: tuple = (0, 0, 100, 100)
    change_threshold: float = 20.0
    check_interval: float = 0.5
    configuration: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringStopped(BaseDomainEvent):
    """Event fired when ROI monitoring stops"""
    
    session_id: str = ""
    roi_id: str = ""
    duration_seconds: float = 0.0
    screenshots_captured: int = 0
    changes_detected: int = 0
    reason: str = "manual"  # manual, error, system


@dataclass
class MonitoringPaused(BaseDomainEvent):
    """Event fired when ROI monitoring is paused"""
    
    session_id: str = ""
    roi_id: str = ""
    reason: str = "manual"


@dataclass
class MonitoringResumed(BaseDomainEvent):
    """Event fired when ROI monitoring is resumed"""
    
    session_id: str = ""
    roi_id: str = ""


@dataclass
class ChangeDetected(BaseDomainEvent):
    """Event fired when a change is detected in ROI"""
    
    session_id: str = ""
    roi_id: str = ""
    change_score: float = 0.0
    threshold: float = 20.0
    screenshot_triggered: bool = False
    screenshot_id: Optional[str] = None
    detection_method: str = "threshold"


@dataclass
class ROIUpdated(BaseDomainEvent):
    """Event fired when ROI configuration is updated"""
    
    roi_id: str = ""
    old_coordinates: Optional[tuple] = None
    new_coordinates: tuple = (0, 0, 100, 100)
    old_threshold: Optional[float] = None
    new_threshold: float = 20.0
    updated_by: str = "system"


@dataclass
class MonitoringError(BaseDomainEvent):
    """Event fired when monitoring encounters an error"""
    
    session_id: str = ""
    roi_id: str = ""
    error_type: str = "capture_failed"
    error_message: str = ""
    is_recoverable: bool = True
    retry_count: int = 0
