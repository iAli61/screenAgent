"""
Monitoring-related Data Transfer Objects
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class MonitoringStartRequest:
    """Request to start monitoring"""
    interval: Optional[float] = None
    roi_enabled: Optional[bool] = None
    roi_x: Optional[int] = None
    roi_y: Optional[int] = None
    roi_width: Optional[int] = None
    roi_height: Optional[int] = None
    change_threshold: Optional[float] = None
    continuous_mode: Optional[bool] = None
    max_screenshots: Optional[int] = None
    duration_seconds: Optional[int] = None


@dataclass
class MonitoringStartResponse:
    """Response after starting monitoring"""
    success: bool
    session_id: Optional[str] = None
    message: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class MonitoringStopRequest:
    """Request to stop monitoring"""
    session_id: Optional[str] = None
    force: Optional[bool] = None


@dataclass
class MonitoringStopResponse:
    """Response after stopping monitoring"""
    success: bool
    session_id: Optional[str] = None
    duration_seconds: Optional[float] = None
    screenshots_captured: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None


@dataclass
class MonitoringStatusResponse:
    """Current monitoring status response"""
    success: bool
    is_monitoring: bool
    session_id: Optional[str] = None
    start_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    screenshots_captured: Optional[int] = None
    last_screenshot_time: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class MonitoringSessionListResponse:
    """Response containing list of monitoring sessions"""
    success: bool
    sessions: List[Dict[str, Any]]
    total_count: int
    active_sessions: int
    error: Optional[str] = None


@dataclass
class MonitoringSessionDetailsResponse:
    """Detailed monitoring session information"""
    success: bool
    session: Optional[Dict[str, Any]] = None
    screenshots: Optional[List[Dict[str, Any]]] = None
    statistics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
