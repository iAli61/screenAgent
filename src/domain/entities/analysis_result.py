"""
Analysis Result domain entity
Represents AI analysis results with metadata and behavior
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


class AnalysisStatus(Enum):
    """Analysis status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisProvider(Enum):
    """AI analysis provider enumeration"""
    OPENAI_GPT4 = "openai_gpt4"
    OPENAI_GPT4_VISION = "openai_gpt4_vision"
    AZURE_AI = "azure_ai"
    CLAUDE = "claude"
    CUSTOM = "custom"


@dataclass
class AnalysisResult:
    """Analysis result domain entity with rich behavior"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    screenshot_id: str = ""
    provider: AnalysisProvider = AnalysisProvider.OPENAI_GPT4_VISION
    model_name: str = "gpt-4o"
    prompt: str = ""
    result_text: str = ""
    confidence_score: Optional[float] = None
    processing_time_ms: Optional[int] = None
    status: AnalysisStatus = AnalysisStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None
    structured_data: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization setup"""
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        
        if isinstance(self.started_at, str):
            self.started_at = datetime.fromisoformat(self.started_at)
        
        if isinstance(self.completed_at, str):
            self.completed_at = datetime.fromisoformat(self.completed_at)
        
        if isinstance(self.status, str):
            self.status = AnalysisStatus(self.status)
        
        if isinstance(self.provider, str):
            self.provider = AnalysisProvider(self.provider)
    
    def start_analysis(self) -> None:
        """Mark analysis as started"""
        self.status = AnalysisStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete_analysis(self, result_text: str, confidence_score: Optional[float] = None, 
                         tokens_used: Optional[int] = None) -> None:
        """Mark analysis as completed with results"""
        self.status = AnalysisStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result_text = result_text
        self.confidence_score = confidence_score
        self.tokens_used = tokens_used
        
        # Calculate processing time
        if self.started_at:
            processing_time = self.completed_at - self.started_at
            self.processing_time_ms = int(processing_time.total_seconds() * 1000)
    
    def fail_analysis(self, error_message: str) -> None:
        """Mark analysis as failed with error"""
        self.status = AnalysisStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
        
        # Calculate processing time even for failures
        if self.started_at:
            processing_time = self.completed_at - self.started_at
            self.processing_time_ms = int(processing_time.total_seconds() * 1000)
    
    def cancel_analysis(self) -> None:
        """Cancel the analysis"""
        self.status = AnalysisStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def add_structured_data(self, key: str, value: Any) -> None:
        """Add structured data extracted from analysis"""
        self.structured_data[key] = value
    
    def extract_entities(self, entities: List[str]) -> None:
        """Extract and store entities found in the analysis"""
        self.add_structured_data('entities', entities)
        
        # Add entities as tags for easy searching
        for entity in entities:
            self.add_tag(f"entity:{entity}")
    
    def extract_sentiment(self, sentiment: str, score: float) -> None:
        """Extract and store sentiment analysis"""
        self.add_structured_data('sentiment', {
            'label': sentiment,
            'score': score
        })
        self.add_tag(f"sentiment:{sentiment}")
    
    def extract_objects(self, objects: List[str]) -> None:
        """Extract and store objects detected in image"""
        self.add_structured_data('objects', objects)
        
        # Add objects as tags
        for obj in objects:
            self.add_tag(f"object:{obj}")
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the analysis result"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the analysis result"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def get_processing_duration(self) -> Optional[str]:
        """Get human-readable processing duration"""
        if not self.processing_time_ms:
            return None
        
        if self.processing_time_ms < 1000:
            return f"{self.processing_time_ms}ms"
        else:
            seconds = self.processing_time_ms / 1000
            return f"{seconds:.2f}s"
    
    def estimate_cost(self, cost_per_token: float = 0.01) -> float:
        """Estimate analysis cost based on tokens used"""
        if not self.tokens_used:
            return 0.0
        
        self.cost_estimate = self.tokens_used * cost_per_token
        return self.cost_estimate
    
    def is_successful(self) -> bool:
        """Check if analysis was successful"""
        return self.status == AnalysisStatus.COMPLETED
    
    def is_finished(self) -> bool:
        """Check if analysis is finished (completed, failed, or cancelled)"""
        return self.status in [AnalysisStatus.COMPLETED, AnalysisStatus.FAILED, AnalysisStatus.CANCELLED]
    
    def get_quality_score(self) -> float:
        """Get analysis quality score based on confidence and processing time"""
        if not self.is_successful() or not self.confidence_score:
            return 0.0
        
        # Base score is confidence
        score = self.confidence_score
        
        # Adjust based on processing time (faster is better up to a point)
        if self.processing_time_ms:
            if self.processing_time_ms < 1000:  # Very fast might be low quality
                score *= 0.9
            elif self.processing_time_ms > 30000:  # Very slow might indicate problems
                score *= 0.8
        
        return min(score, 1.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'screenshot_id': self.screenshot_id,
            'provider': self.provider.value,
            'model_name': self.model_name,
            'prompt': self.prompt,
            'result_text': self.result_text,
            'confidence_score': self.confidence_score,
            'processing_time_ms': self.processing_time_ms,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'tokens_used': self.tokens_used,
            'cost_estimate': self.cost_estimate,
            'structured_data': self.structured_data,
            'tags': self.tags,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalysisResult':
        """Create AnalysisResult from dictionary"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            screenshot_id=data.get('screenshot_id', ''),
            provider=AnalysisProvider(data.get('provider', 'openai_gpt4_vision')),
            model_name=data.get('model_name', 'gpt-4o'),
            prompt=data.get('prompt', ''),
            result_text=data.get('result_text', ''),
            confidence_score=data.get('confidence_score'),
            processing_time_ms=data.get('processing_time_ms'),
            status=AnalysisStatus(data.get('status', 'pending')),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at', datetime.now()),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            error_message=data.get('error_message'),
            tokens_used=data.get('tokens_used'),
            cost_estimate=data.get('cost_estimate'),
            structured_data=data.get('structured_data', {}),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {})
        )
