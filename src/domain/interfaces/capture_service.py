"""
Capture Service Interface
Defines the contract for screenshot capture operations
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

from ..value_objects.coordinates import Rectangle


@dataclass
class CaptureResult:
    """Result of a capture operation"""
    success: bool
    data: Optional[bytes] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ICaptureService(ABC):
    """Interface for screenshot capture operations"""
    
    @abstractmethod
    async def capture_full_screen(
        self, 
        monitor_id: Optional[int] = None
    ) -> CaptureResult:
        """
        Capture full screen screenshot
        
        Args:
            monitor_id: Optional monitor identifier for multi-monitor setup
            
        Returns:
            CaptureResult with captured image data
        """
        pass
    
    @abstractmethod
    async def capture_region(
        self, 
        region: Rectangle,
        monitor_id: Optional[int] = None
    ) -> CaptureResult:
        """
        Capture screenshot of specific region
        
        Args:
            region: Rectangle defining the capture area
            monitor_id: Optional monitor identifier
            
        Returns:
            CaptureResult with captured region data
        """
        pass
    
    @abstractmethod
    async def capture_roi(
        self, 
        roi: Tuple[int, int, int, int]
    ) -> CaptureResult:
        """
        Capture screenshot of specific ROI coordinates
        
        Args:
            roi: ROI coordinates as (left, top, right, bottom)
            
        Returns:
            CaptureResult with captured ROI data
        """
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the capture service
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up capture service resources"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get capabilities of the capture service
        
        Returns:
            Dictionary describing service capabilities
        """
        pass
