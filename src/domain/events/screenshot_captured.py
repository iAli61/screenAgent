"""
Domain events for ScreenAgent
Events represent something important that happened in the domain
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


@dataclass
class BaseDomainEvent:
    """Base class for all domain events"""
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.now)
    event_type: str = field(init=False)
    aggregate_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set event type from class name"""
        self.event_type = self.__class__.__name__


@dataclass
class ScreenshotCaptured(BaseDomainEvent):
    """Event fired when a screenshot is captured"""
    
    screenshot_id: str = ""
    file_path: str = ""
    roi_coordinates: Optional[tuple] = None
    capture_method: str = "manual"
    monitor_id: Optional[int] = None
    size_bytes: int = 0
    width: int = 0
    height: int = 0


@dataclass
class ScreenshotAnalysisStarted(BaseDomainEvent):
    """Event fired when screenshot analysis begins"""
    
    screenshot_id: str = ""
    analysis_id: str = ""
    provider: str = ""
    model_name: str = ""
    prompt: str = ""


@dataclass
class ScreenshotAnalysisCompleted(BaseDomainEvent):
    """Event fired when screenshot analysis completes"""
    
    screenshot_id: str = ""
    analysis_id: str = ""
    result_text: str = ""
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    success: bool = True


@dataclass
class ScreenshotAnalysisFailed(BaseDomainEvent):
    """Event fired when screenshot analysis fails"""
    
    screenshot_id: str = ""
    analysis_id: str = ""
    error_message: str = ""
    provider: str = ""
    model_name: str = ""
