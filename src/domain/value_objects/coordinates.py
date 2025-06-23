"""
Coordinates value object
Immutable coordinate representation with validation
"""
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Coordinates:
    """Immutable coordinates value object"""
    
    x: int
    y: int
    
    def __post_init__(self):
        """Validate coordinates"""
        if self.x < 0 or self.y < 0:
            raise ValueError(f"Coordinates must be non-negative: ({self.x}, {self.y})")
    
    def to_tuple(self) -> Tuple[int, int]:
        """Convert to tuple"""
        return (self.x, self.y)
    
    def distance_to(self, other: 'Coordinates') -> float:
        """Calculate distance to another coordinate"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def translate(self, dx: int, dy: int) -> 'Coordinates':
        """Create new coordinates translated by dx, dy"""
        return Coordinates(self.x + dx, self.y + dy)


@dataclass(frozen=True)
class Rectangle:
    """Immutable rectangle value object"""
    
    left: int
    top: int
    right: int
    bottom: int
    
    def __post_init__(self):
        """Validate rectangle"""
        if self.left >= self.right:
            raise ValueError(f"Left ({self.left}) must be less than right ({self.right})")
        
        if self.top >= self.bottom:
            raise ValueError(f"Top ({self.top}) must be less than bottom ({self.bottom})")
        
        if self.left < 0 or self.top < 0:
            raise ValueError(f"Rectangle coordinates must be non-negative")
    
    @property
    def width(self) -> int:
        """Rectangle width"""
        return self.right - self.left
    
    @property
    def height(self) -> int:
        """Rectangle height"""
        return self.bottom - self.top
    
    @property
    def area(self) -> int:
        """Rectangle area"""
        return self.width * self.height
    
    @property
    def center(self) -> Coordinates:
        """Rectangle center"""
        return Coordinates(
            (self.left + self.right) // 2,
            (self.top + self.bottom) // 2
        )
    
    @property
    def top_left(self) -> Coordinates:
        """Top-left corner"""
        return Coordinates(self.left, self.top)
    
    @property
    def bottom_right(self) -> Coordinates:
        """Bottom-right corner"""
        return Coordinates(self.right, self.bottom)
    
    def contains_point(self, point: Coordinates) -> bool:
        """Check if rectangle contains point"""
        return (self.left <= point.x <= self.right and 
                self.top <= point.y <= self.bottom)
    
    def intersects(self, other: 'Rectangle') -> bool:
        """Check if rectangle intersects with another"""
        return not (self.right <= other.left or other.right <= self.left or
                   self.bottom <= other.top or other.bottom <= self.top)
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Convert to tuple (left, top, right, bottom)"""
        return (self.left, self.top, self.right, self.bottom)
    
    @classmethod
    def from_coordinates(cls, top_left: Coordinates, bottom_right: Coordinates) -> 'Rectangle':
        """Create rectangle from two coordinates"""
        return cls(top_left.x, top_left.y, bottom_right.x, bottom_right.y)
    
    @classmethod
    def from_center_and_size(cls, center: Coordinates, width: int, height: int) -> 'Rectangle':
        """Create rectangle from center point and size"""
        half_width = width // 2
        half_height = height // 2
        
        return cls(
            center.x - half_width,
            center.y - half_height,
            center.x + half_width,
            center.y + half_height
        )
