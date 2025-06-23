"""
Timestamp value object
Immutable timestamp representation with utility methods
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class Timestamp:
    """Immutable timestamp value object"""
    
    value: datetime
    
    def __post_init__(self):
        """Ensure timezone awareness"""
        if self.value.tzinfo is None:
            # Assume UTC if no timezone provided
            object.__setattr__(self, 'value', self.value.replace(tzinfo=timezone.utc))
    
    @classmethod
    def now(cls) -> 'Timestamp':
        """Create timestamp for current time"""
        return cls(datetime.now(timezone.utc))
    
    @classmethod
    def from_iso(cls, iso_string: str) -> 'Timestamp':
        """Create timestamp from ISO string"""
        try:
            dt = datetime.fromisoformat(iso_string)
            return cls(dt)
        except ValueError as e:
            raise ValueError(f"Invalid ISO timestamp: {iso_string}") from e
    
    @classmethod
    def from_unix(cls, unix_timestamp: float) -> 'Timestamp':
        """Create timestamp from Unix timestamp"""
        dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
        return cls(dt)
    
    def to_iso(self) -> str:
        """Convert to ISO string"""
        return self.value.isoformat()
    
    def to_unix(self) -> float:
        """Convert to Unix timestamp"""
        return self.value.timestamp()
    
    def to_display(self) -> str:
        """Convert to human-readable display format"""
        return self.value.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def to_filename(self) -> str:
        """Convert to filename-safe format"""
        return self.value.strftime("%Y%m%d_%H%M%S")
    
    def is_before(self, other: 'Timestamp') -> bool:
        """Check if this timestamp is before another"""
        return self.value < other.value
    
    def is_after(self, other: 'Timestamp') -> bool:
        """Check if this timestamp is after another"""
        return self.value > other.value
    
    def is_same_day(self, other: 'Timestamp') -> bool:
        """Check if this timestamp is on the same day as another"""
        return self.value.date() == other.value.date()
    
    def add_seconds(self, seconds: int) -> 'Timestamp':
        """Create new timestamp with added seconds"""
        from datetime import timedelta
        return Timestamp(self.value + timedelta(seconds=seconds))
    
    def add_minutes(self, minutes: int) -> 'Timestamp':
        """Create new timestamp with added minutes"""
        return self.add_seconds(minutes * 60)
    
    def add_hours(self, hours: int) -> 'Timestamp':
        """Create new timestamp with added hours"""
        return self.add_seconds(hours * 3600)
    
    def subtract(self, other: 'Timestamp') -> float:
        """Get difference in seconds between timestamps"""
        return (self.value - other.value).total_seconds()


@dataclass(frozen=True)
class TimeRange:
    """Immutable time range value object"""
    
    start: Timestamp
    end: Timestamp
    
    def __post_init__(self):
        """Validate time range"""
        if self.start.is_after(self.end):
            raise ValueError(f"Start time must be before end time")
    
    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds"""
        return self.end.subtract(self.start)
    
    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes"""
        return self.duration_seconds / 60
    
    @property
    def duration_hours(self) -> float:
        """Get duration in hours"""
        return self.duration_seconds / 3600
    
    def contains(self, timestamp: Timestamp) -> bool:
        """Check if timestamp is within this range"""
        return (not timestamp.is_before(self.start) and 
                not timestamp.is_after(self.end))
    
    def overlaps(self, other: 'TimeRange') -> bool:
        """Check if this range overlaps with another"""
        return (not self.end.is_before(other.start) and 
                not other.end.is_before(self.start))
    
    def to_display(self) -> str:
        """Convert to human-readable display format"""
        return f"{self.start.to_display()} - {self.end.to_display()}"
