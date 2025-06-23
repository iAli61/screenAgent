"""
System domain events
Events related to system-level operations and lifecycle
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, List
import uuid
from .screenshot_captured import BaseDomainEvent


@dataclass
class SystemStarted(BaseDomainEvent):
    """Event fired when the system starts up"""
    
    version: str = "1.0.0"
    configuration: Dict[str, Any] = field(default_factory=dict)
    modules_loaded: List[str] = field(default_factory=list)
    startup_time_ms: float = 0.0


@dataclass
class SystemShutdown(BaseDomainEvent):
    """Event fired when the system shuts down"""
    
    reason: str = "manual"  # manual, error, signal
    uptime_seconds: float = 0.0
    sessions_cleaned: int = 0
    files_cleaned: int = 0


@dataclass
class ConfigurationChanged(BaseDomainEvent):
    """Event fired when system configuration changes"""
    
    config_section: str = ""
    old_values: Dict[str, Any] = field(default_factory=dict)
    new_values: Dict[str, Any] = field(default_factory=dict)
    changed_by: str = "system"
    restart_required: bool = False


@dataclass
class StorageCleanup(BaseDomainEvent):
    """Event fired when storage cleanup occurs"""
    
    files_deleted: int = 0
    bytes_freed: int = 0
    directories_removed: int = 0
    cleanup_type: str = "scheduled"  # scheduled, manual, low_space


@dataclass
class HealthCheckPerformed(BaseDomainEvent):
    """Event fired when health check is performed"""
    
    status: str = "healthy"  # healthy, degraded, unhealthy
    checks_passed: int = 0
    checks_failed: int = 0
    response_time_ms: float = 0.0
    issues: List[str] = field(default_factory=list)


@dataclass
class ResourceLimit(BaseDomainEvent):
    """Event fired when resource limits are approached/exceeded"""
    
    resource_type: str = "memory"  # memory, disk, cpu
    current_usage: float = 0.0
    limit: float = 100.0
    usage_percentage: float = 0.0
    action_taken: str = "none"  # none, warning, cleanup, throttle


@dataclass
class ServiceError(BaseDomainEvent):
    """Event fired when a service encounters an error"""
    
    service_name: str = ""
    error_type: str = "exception"
    error_message: str = ""
    stack_trace: Optional[str] = None
    is_recoverable: bool = True
    retry_count: int = 0
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChangeDetectionEvent(BaseDomainEvent):
    """Event fired when a change is detected in monitoring"""
    
    change_score: float = 0.0
    threshold_used: float = 20.0
    strategy_name: str = ""
    roi_coordinates: tuple = ()
    metadata: Dict[str, Any] = field(default_factory=dict)
    baseline_updated: bool = False


@dataclass
class ChangeDetectionStartedEvent(BaseDomainEvent):
    """Event fired when change detection monitoring starts"""
    
    strategy_name: str = ""
    roi_coordinates: tuple = ()
    check_interval: float = 1.0
    threshold: float = 20.0
    baseline_initialized: bool = False


@dataclass
class ChangeDetectionStoppedEvent(BaseDomainEvent):
    """Event fired when change detection monitoring stops"""
    
    duration_seconds: float = 0.0
    total_checks: int = 0
    changes_detected: int = 0
    strategy_name: str = ""
    reason: str = "manual"  # manual, error, shutdown


@dataclass
class ChangeDetectionStrategyChangedEvent(BaseDomainEvent):
    """Event fired when the change detection strategy is changed"""
    
    old_strategy: str = ""
    new_strategy: str = ""
    reason: str = "manual"
    baseline_reset: bool = True
    configuration: Dict[str, Any] = field(default_factory=dict)
