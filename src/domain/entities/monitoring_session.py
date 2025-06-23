"""
Monitoring Session domain entity
Represents a ROI monitoring session with statistics and behavior
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


class SessionStatus(Enum):
    """Monitoring session status"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class MonitoringStatistics:
    """Statistics for a monitoring session"""
    screenshots_captured: int = 0
    changes_detected: int = 0
    false_positives: int = 0
    average_change_score: float = 0.0
    max_change_score: float = 0.0
    min_change_score: float = 0.0
    total_monitoring_time: timedelta = field(default_factory=lambda: timedelta(0))
    
    def update_change_score(self, score: float) -> None:
        """Update change score statistics"""
        self.changes_detected += 1
        
        # Update average
        if self.changes_detected == 1:
            self.average_change_score = score
        else:
            self.average_change_score = (
                (self.average_change_score * (self.changes_detected - 1) + score) / 
                self.changes_detected
            )
        
        # Update min/max
        if self.changes_detected == 1:
            self.max_change_score = score
            self.min_change_score = score
        else:
            self.max_change_score = max(self.max_change_score, score)
            self.min_change_score = min(self.min_change_score, score)
    
    def increment_screenshots(self) -> None:
        """Increment screenshot count"""
        self.screenshots_captured += 1
    
    def increment_false_positives(self) -> None:
        """Increment false positive count"""
        self.false_positives += 1


@dataclass
class MonitoringSession:
    """Monitoring session domain entity with behavior and statistics"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    roi_id: str = ""
    name: str = "Monitoring Session"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None
    status: SessionStatus = SessionStatus.CREATED
    statistics: MonitoringStatistics = field(default_factory=MonitoringStatistics)
    screenshot_ids: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization setup"""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        
        if isinstance(self.started_at, str):
            self.started_at = datetime.fromisoformat(self.started_at)
        
        if isinstance(self.stopped_at, str):
            self.stopped_at = datetime.fromisoformat(self.stopped_at)
        
        if isinstance(self.status, str):
            self.status = SessionStatus(self.status)
    
    def start(self) -> None:
        """Start the monitoring session"""
        if self.status == SessionStatus.RUNNING:
            raise ValueError("Session is already running")
        
        self.status = SessionStatus.RUNNING
        self.started_at = datetime.now()
        self.stopped_at = None
    
    def stop(self) -> None:
        """Stop the monitoring session"""
        if self.status not in [SessionStatus.RUNNING, SessionStatus.PAUSED]:
            raise ValueError("Session is not running or paused")
        
        self.status = SessionStatus.STOPPED
        self.stopped_at = datetime.now()
        
        # Update total monitoring time
        if self.started_at:
            self.statistics.total_monitoring_time = self.stopped_at - self.started_at
    
    def pause(self) -> None:
        """Pause the monitoring session"""
        if self.status != SessionStatus.RUNNING:
            raise ValueError("Session is not running")
        
        self.status = SessionStatus.PAUSED
    
    def resume(self) -> None:
        """Resume the monitoring session"""
        if self.status != SessionStatus.PAUSED:
            raise ValueError("Session is not paused")
        
        self.status = SessionStatus.RUNNING
    
    def add_screenshot(self, screenshot_id: str) -> None:
        """Add a screenshot to this session"""
        if screenshot_id not in self.screenshot_ids:
            self.screenshot_ids.append(screenshot_id)
            self.statistics.increment_screenshots()
    
    def record_change_detection(self, change_score: float, screenshot_id: str) -> None:
        """Record a change detection event"""
        self.statistics.update_change_score(change_score)
        self.add_screenshot(screenshot_id)
    
    def record_false_positive(self) -> None:
        """Record a false positive detection"""
        self.statistics.increment_false_positives()
    
    def add_error(self, error_message: str, error_type: str = "general") -> None:
        """Add an error to the session"""
        error_entry = {
            'timestamp': datetime.now().isoformat(),
            'message': error_message,
            'type': error_type
        }
        self.errors.append(error_entry)
        
        # Mark session as error if critical error
        if error_type in ['critical', 'fatal']:
            self.status = SessionStatus.ERROR
    
    def get_duration(self) -> Optional[timedelta]:
        """Get session duration"""
        if not self.started_at:
            return None
        
        end_time = self.stopped_at or datetime.now()
        return end_time - self.started_at
    
    def get_uptime_percentage(self) -> float:
        """Get uptime percentage (running vs total time)"""
        duration = self.get_duration()
        if not duration or duration.total_seconds() == 0:
            return 0.0
        
        return (self.statistics.total_monitoring_time.total_seconds() / duration.total_seconds()) * 100
    
    def get_detection_rate(self) -> float:
        """Get change detection rate (changes per hour)"""
        if not self.statistics.total_monitoring_time.total_seconds():
            return 0.0
        
        hours = self.statistics.total_monitoring_time.total_seconds() / 3600
        return self.statistics.changes_detected / hours if hours > 0 else 0.0
    
    def get_false_positive_rate(self) -> float:
        """Get false positive rate as percentage"""
        total_detections = self.statistics.changes_detected + self.statistics.false_positives
        if total_detections == 0:
            return 0.0
        
        return (self.statistics.false_positives / total_detections) * 100
    
    def is_active(self) -> bool:
        """Check if session is currently active"""
        return self.status in [SessionStatus.RUNNING, SessionStatus.PAUSED]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'roi_id': self.roi_id,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'stopped_at': self.stopped_at.isoformat() if self.stopped_at else None,
            'status': self.status.value,
            'statistics': {
                'screenshots_captured': self.statistics.screenshots_captured,
                'changes_detected': self.statistics.changes_detected,
                'false_positives': self.statistics.false_positives,
                'average_change_score': self.statistics.average_change_score,
                'max_change_score': self.statistics.max_change_score,
                'min_change_score': self.statistics.min_change_score,
                'total_monitoring_time': self.statistics.total_monitoring_time.total_seconds()
            },
            'screenshot_ids': self.screenshot_ids,
            'configuration': self.configuration,
            'errors': self.errors,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MonitoringSession':
        """Create MonitoringSession from dictionary"""
        stats_data = data.get('statistics', {})
        statistics = MonitoringStatistics(
            screenshots_captured=stats_data.get('screenshots_captured', 0),
            changes_detected=stats_data.get('changes_detected', 0),
            false_positives=stats_data.get('false_positives', 0),
            average_change_score=stats_data.get('average_change_score', 0.0),
            max_change_score=stats_data.get('max_change_score', 0.0),
            min_change_score=stats_data.get('min_change_score', 0.0),
            total_monitoring_time=timedelta(seconds=stats_data.get('total_monitoring_time', 0))
        )
        
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            roi_id=data.get('roi_id', ''),
            name=data.get('name', 'Monitoring Session'),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at', datetime.now()),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            stopped_at=datetime.fromisoformat(data['stopped_at']) if data.get('stopped_at') else None,
            status=SessionStatus(data.get('status', 'created')),
            statistics=statistics,
            screenshot_ids=data.get('screenshot_ids', []),
            configuration=data.get('configuration', {}),
            errors=data.get('errors', []),
            metadata=data.get('metadata', {})
        )
