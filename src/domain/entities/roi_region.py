"""
ROI (Region of Interest) domain entity
Represents a monitored screen region with validation and behavior
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from enum import Enum
import uuid


class ROIStatus(Enum):
    """ROI monitoring status"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class ROIRegion:
    """ROI region domain entity with validation and behavior"""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Unnamed ROI"
    coordinates: Tuple[int, int, int, int] = (0, 0, 100, 100)  # (left, top, right, bottom)
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    status: ROIStatus = ROIStatus.INACTIVE
    change_threshold: float = 20.0
    check_interval: float = 0.5
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation"""
        self.validate_coordinates()
        
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        
        if isinstance(self.last_modified, str):
            self.last_modified = datetime.fromisoformat(self.last_modified)
        
        if isinstance(self.status, str):
            self.status = ROIStatus(self.status)
    
    def validate_coordinates(self) -> None:
        """Validate ROI coordinates"""
        left, top, right, bottom = self.coordinates
        
        if left >= right:
            raise ValueError(f"Invalid ROI: left ({left}) must be less than right ({right})")
        
        if top >= bottom:
            raise ValueError(f"Invalid ROI: top ({top}) must be less than bottom ({bottom})")
        
        if left < 0 or top < 0:
            raise ValueError(f"Invalid ROI: coordinates cannot be negative ({left}, {top})")
        
        min_size = 10
        if (right - left) < min_size or (bottom - top) < min_size:
            raise ValueError(f"Invalid ROI: minimum size is {min_size}x{min_size} pixels")
    
    def update_coordinates(self, coordinates: Tuple[int, int, int, int]) -> None:
        """Update ROI coordinates with validation"""
        old_coordinates = self.coordinates
        self.coordinates = coordinates
        
        try:
            self.validate_coordinates()
            self.last_modified = datetime.now()
        except ValueError:
            # Rollback on validation failure
            self.coordinates = old_coordinates
            raise
    
    def get_width(self) -> int:
        """Get ROI width"""
        return self.coordinates[2] - self.coordinates[0]
    
    def get_height(self) -> int:
        """Get ROI height"""
        return self.coordinates[3] - self.coordinates[1]
    
    def get_area(self) -> int:
        """Get ROI area in pixels"""
        return self.get_width() * self.get_height()
    
    def get_center(self) -> Tuple[int, int]:
        """Get ROI center coordinates"""
        left, top, right, bottom = self.coordinates
        return ((left + right) // 2, (top + bottom) // 2)
    
    def contains_point(self, x: int, y: int) -> bool:
        """Check if point is within ROI"""
        left, top, right, bottom = self.coordinates
        return left <= x <= right and top <= y <= bottom
    
    def overlaps_with(self, other: 'ROIRegion') -> bool:
        """Check if this ROI overlaps with another"""
        left1, top1, right1, bottom1 = self.coordinates
        left2, top2, right2, bottom2 = other.coordinates
        
        return not (right1 <= left2 or right2 <= left1 or bottom1 <= top2 or bottom2 <= top1)
    
    def activate(self) -> None:
        """Activate ROI monitoring"""
        self.status = ROIStatus.ACTIVE
        self.last_modified = datetime.now()
    
    def deactivate(self) -> None:
        """Deactivate ROI monitoring"""
        self.status = ROIStatus.INACTIVE
        self.last_modified = datetime.now()
    
    def pause(self) -> None:
        """Pause ROI monitoring"""
        self.status = ROIStatus.PAUSED
        self.last_modified = datetime.now()
    
    def mark_error(self, error_message: str) -> None:
        """Mark ROI as having an error"""
        self.status = ROIStatus.ERROR
        self.metadata['last_error'] = error_message
        self.metadata['error_timestamp'] = datetime.now().isoformat()
        self.last_modified = datetime.now()
    
    def update_threshold(self, threshold: float) -> None:
        """Update change detection threshold"""
        if not 0 < threshold <= 100:
            raise ValueError("Threshold must be between 0 and 100")
        
        self.change_threshold = threshold
        self.last_modified = datetime.now()
    
    def update_interval(self, interval: float) -> None:
        """Update check interval"""
        if interval <= 0:
            raise ValueError("Check interval must be positive")
        
        self.check_interval = interval
        self.last_modified = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'coordinates': list(self.coordinates),
            'created_at': self.created_at.isoformat(),
            'last_modified': self.last_modified.isoformat(),
            'status': self.status.value,
            'change_threshold': self.change_threshold,
            'check_interval': self.check_interval,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ROIRegion':
        """Create ROIRegion from dictionary"""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            name=data.get('name', 'Unnamed ROI'),
            coordinates=tuple(data.get('coordinates', [0, 0, 100, 100])),
            created_at=datetime.fromisoformat(data['created_at']) if isinstance(data.get('created_at'), str) else data.get('created_at', datetime.now()),
            last_modified=datetime.fromisoformat(data['last_modified']) if isinstance(data.get('last_modified'), str) else data.get('last_modified', datetime.now()),
            status=ROIStatus(data.get('status', 'inactive')),
            change_threshold=data.get('change_threshold', 20.0),
            check_interval=data.get('check_interval', 0.5),
            metadata=data.get('metadata', {})
        )
