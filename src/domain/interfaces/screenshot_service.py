"""
Screenshot Service Interface
Defines the contract for screenshot capture and management
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pathlib import Path

from ..entities.screenshot import Screenshot
from ..entities.roi_region import ROIRegion
from ..value_objects.coordinates import Rectangle


class IScreenshotService(ABC):
    """Interface for screenshot capture and management services"""
    
    @abstractmethod
    async def capture_full_screen(
        self, 
        monitor_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Screenshot:
        """
        Capture full screen screenshot
        
        Args:
            monitor_id: Optional monitor identifier for multi-monitor setup
            metadata: Optional metadata to include with screenshot
            
        Returns:
            Screenshot entity with captured image and metadata
        """
        pass
    
    @abstractmethod
    async def capture_region(
        self, 
        region: Rectangle,
        monitor_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Screenshot:
        """
        Capture screenshot of specific region
        
        Args:
            region: Rectangle defining the capture area
            monitor_id: Optional monitor identifier
            metadata: Optional metadata to include with screenshot
            
        Returns:
            Screenshot entity with captured region
        """
        pass
    
    @abstractmethod
    async def capture_roi(
        self, 
        roi: ROIRegion,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Screenshot:
        """
        Capture screenshot of ROI region
        
        Args:
            roi: ROI region entity
            metadata: Optional metadata to include with screenshot
            
        Returns:
            Screenshot entity with captured ROI
        """
        pass
    
    @abstractmethod
    async def save_screenshot(
        self, 
        screenshot: Screenshot, 
        directory_path: Optional[Path] = None
    ) -> Path:
        """
        Save screenshot to storage
        
        Args:
            screenshot: Screenshot entity to save
            directory_path: Optional custom directory path
            
        Returns:
            Path where screenshot was saved
        """
        pass
    
    @abstractmethod
    async def get_screenshot(self, screenshot_id: str) -> Optional[Screenshot]:
        """
        Retrieve screenshot by ID
        
        Args:
            screenshot_id: Unique screenshot identifier
            
        Returns:
            Screenshot entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_screenshots(
        self, 
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Screenshot]:
        """
        List screenshots with optional filtering
        
        Args:
            session_id: Optional filter by session
            limit: Maximum number of screenshots to return
            offset: Number of screenshots to skip
            
        Returns:
            List of screenshot entities
        """
        pass
    
    @abstractmethod
    async def delete_screenshot(self, screenshot_id: str) -> bool:
        """
        Delete screenshot by ID
        
        Args:
            screenshot_id: Unique screenshot identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def cleanup_old_screenshots(
        self, 
        max_age_days: int = 30,
        max_count: Optional[int] = None
    ) -> int:
        """
        Clean up old screenshots based on age and count
        
        Args:
            max_age_days: Maximum age in days to keep screenshots
            max_count: Maximum number of screenshots to keep
            
        Returns:
            Number of screenshots deleted
        """
        pass
