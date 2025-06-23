"""
Monitoring Service Interface
Defines the contract for ROI monitoring operations
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Callable
from asyncio import Task

from ..entities.roi_region import ROIRegion
from ..entities.monitoring_session import MonitoringSession
from ..entities.screenshot import Screenshot


class IMonitoringService(ABC):
    """Interface for ROI monitoring services"""
    
    @abstractmethod
    async def start_monitoring(
        self, 
        roi: ROIRegion,
        change_threshold: float = 20.0,
        check_interval: float = 0.5,
        on_change_callback: Optional[Callable] = None
    ) -> MonitoringSession:
        """
        Start monitoring an ROI region for changes
        
        Args:
            roi: ROI region to monitor
            change_threshold: Threshold for change detection (0-100)
            check_interval: Time between checks in seconds
            on_change_callback: Optional callback for change events
            
        Returns:
            MonitoringSession entity
        """
        pass
    
    @abstractmethod
    async def stop_monitoring(self, session_id: str) -> bool:
        """
        Stop monitoring session
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if stopped successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def pause_monitoring(self, session_id: str) -> bool:
        """
        Pause monitoring session
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if paused successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def resume_monitoring(self, session_id: str) -> bool:
        """
        Resume monitoring session
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if resumed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def update_monitoring_config(
        self, 
        session_id: str,
        change_threshold: Optional[float] = None,
        check_interval: Optional[float] = None
    ) -> bool:
        """
        Update monitoring configuration
        
        Args:
            session_id: Unique session identifier
            change_threshold: New threshold for change detection
            check_interval: New interval between checks
            
        Returns:
            True if updated successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_monitoring_session(self, session_id: str) -> Optional[MonitoringSession]:
        """
        Get monitoring session by ID
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            MonitoringSession entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def list_active_sessions(self) -> List[MonitoringSession]:
        """
        List all active monitoring sessions
        
        Returns:
            List of active MonitoringSession entities
        """
        pass
    
    @abstractmethod
    async def get_session_screenshots(
        self, 
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Screenshot]:
        """
        Get screenshots captured during monitoring session
        
        Args:
            session_id: Unique session identifier
            limit: Maximum number of screenshots to return
            
        Returns:
            List of Screenshot entities
        """
        pass
    
    @abstractmethod
    async def get_change_history(
        self, 
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get change detection history for session
        
        Args:
            session_id: Unique session identifier
            limit: Maximum number of changes to return
            
        Returns:
            List of change detection events
        """
        pass
    
    @abstractmethod
    async def cleanup_completed_sessions(self, max_age_days: int = 7) -> int:
        """
        Clean up completed monitoring sessions
        
        Args:
            max_age_days: Maximum age in days to keep sessions
            
        Returns:
            Number of sessions cleaned up
        """
        pass
