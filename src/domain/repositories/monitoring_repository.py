"""
Monitoring Repository Interface
Abstract data access for monitoring session entities
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..entities.monitoring_session import MonitoringSession


class IMonitoringRepository(ABC):
    """Interface for monitoring session data access operations"""
    
    @abstractmethod
    async def create(self, session: MonitoringSession) -> MonitoringSession:
        """
        Create a new monitoring session record
        
        Args:
            session: MonitoringSession entity to create
            
        Returns:
            Created session entity with any generated fields
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: str) -> Optional[MonitoringSession]:
        """
        Get monitoring session by ID
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            MonitoringSession entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, session: MonitoringSession) -> MonitoringSession:
        """
        Update existing monitoring session record
        
        Args:
            session: MonitoringSession entity to update
            
        Returns:
            Updated session entity
        """
        pass
    
    @abstractmethod
    async def delete(self, session_id: str) -> bool:
        """
        Delete monitoring session by ID
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_all(
        self, 
        limit: Optional[int] = None, 
        offset: int = 0
    ) -> List[MonitoringSession]:
        """
        List all monitoring sessions with pagination
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            List of monitoring session entities
        """
        pass
    
    @abstractmethod
    async def find_by_status(self, status: str) -> List[MonitoringSession]:
        """
        Find monitoring sessions by status
        
        Args:
            status: Session status (running, paused, stopped, error)
            
        Returns:
            List of sessions with matching status
        """
        pass
    
    @abstractmethod
    async def find_by_roi(self, roi_id: str) -> List[MonitoringSession]:
        """
        Find monitoring sessions by ROI region ID
        
        Args:
            roi_id: ROI region identifier
            
        Returns:
            List of sessions monitoring the ROI
        """
        pass
    
    @abstractmethod
    async def find_active_sessions(self) -> List[MonitoringSession]:
        """
        Find all active monitoring sessions
        
        Returns:
            List of active (running or paused) sessions
        """
        pass
    
    @abstractmethod
    async def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[MonitoringSession]:
        """
        Find monitoring sessions within date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of sessions in date range
        """
        pass
    
    @abstractmethod
    async def find_completed_sessions(
        self, 
        max_age_days: Optional[int] = None
    ) -> List[MonitoringSession]:
        """
        Find completed monitoring sessions
        
        Args:
            max_age_days: Optional filter by age in days
            
        Returns:
            List of completed sessions
        """
        pass
    
    @abstractmethod
    async def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics for a monitoring session
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dictionary with session statistics
        """
        pass
    
    @abstractmethod
    async def get_roi_session_count(self, roi_id: str) -> int:
        """
        Get count of sessions for a specific ROI
        
        Args:
            roi_id: ROI region identifier
            
        Returns:
            Number of sessions for the ROI
        """
        pass
    
    @abstractmethod
    async def cleanup_old_sessions(self, max_age_days: int) -> int:
        """
        Clean up old monitoring sessions
        
        Args:
            max_age_days: Maximum age in days
            
        Returns:
            Number of sessions deleted
        """
        pass
    
    @abstractmethod
    async def get_total_monitoring_time(self) -> float:
        """
        Get total monitoring time across all sessions
        
        Returns:
            Total monitoring time in seconds
        """
        pass
