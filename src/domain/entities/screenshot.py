"""
Domain entities for ScreenAgent
Rich domain objects with behavior and business rules
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


class ScreenshotStatus(Enum):
    """Screenshot status enumeration"""
    CAPTURED = "captured"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    FAILED = "failed"


class CaptureMethod(Enum):
    """Screenshot capture method enumeration"""
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SCHEDULED = "scheduled"


@dataclass
class Screenshot:
    """Screenshot domain entity with rich behavior"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    file_path: Optional[str] = None
    roi_coordinates: Optional[tuple] = None
    size_bytes: int = 0
    width: int = 0
    height: int = 0
    format: str = "PNG"  # Image format (PNG, JPEG, etc.)
    status: ScreenshotStatus = ScreenshotStatus.CAPTURED
    capture_method: CaptureMethod = CaptureMethod.MANUAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    analysis_results: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Temporary field for binary data - TODO: move to storage layer in pure clean architecture
    data: Optional[bytes] = None
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        if isinstance(self.timestamp, str):
            self.timestamp = datetime.fromisoformat(self.timestamp)
        
        if isinstance(self.status, str):
            self.status = ScreenshotStatus(self.status)
        
        if isinstance(self.capture_method, str):
            self.capture_method = CaptureMethod(self.capture_method)
    
    def mark_as_analyzed(self, analysis_result: Dict[str, Any]) -> None:
        """Mark screenshot as analyzed with results"""
        self.status = ScreenshotStatus.ANALYZED
        self.analysis_results.append({
            'timestamp': datetime.now().isoformat(),
            'result': analysis_result
        })
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the screenshot"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the screenshot"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def update_metadata(self, key: str, value: Any) -> None:
        """Update screenshot metadata"""
        self.metadata[key] = value
    
    def get_display_name(self) -> str:
        """Get human-readable display name"""
        return f"Screenshot_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"
    
    def is_roi_screenshot(self) -> bool:
        """Check if this is a ROI screenshot"""
        return self.roi_coordinates is not None
    
    def get_file_size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.size_bytes / (1024 * 1024)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'file_path': self.file_path,
            'roi_coordinates': self.roi_coordinates,
            'size_bytes': self.size_bytes,
            'width': self.width,
            'height': self.height,
            'status': self.status.value,
            'capture_method': self.capture_method.value,
            'metadata': self.metadata,
            'analysis_results': self.analysis_results,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Screenshot':
        """Create Screenshot from dictionary"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            timestamp=datetime.fromisoformat(data['timestamp']) if isinstance(data.get('timestamp'), str) else data.get('timestamp', datetime.now()),
            file_path=data.get('file_path'),
            roi_coordinates=tuple(data['roi_coordinates']) if data.get('roi_coordinates') else None,
            size_bytes=data.get('size_bytes', 0),
            width=data.get('width', 0),
            height=data.get('height', 0),
            status=ScreenshotStatus(data.get('status', 'captured')),
            capture_method=CaptureMethod(data.get('capture_method', 'manual')),
            metadata=data.get('metadata', {}),
            analysis_results=data.get('analysis_results', []),
            tags=data.get('tags', [])
        )
