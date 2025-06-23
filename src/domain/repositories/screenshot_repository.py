"""
Screenshot Repository Interface
Abstract data access for screenshot entities
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from ..entities.screenshot import Screenshot


class IScreenshotRepository(ABC):
    """Interface for screenshot data access operations"""
    
    @abstractmethod
    async def create(self, screenshot: Screenshot) -> Screenshot:
        """
        Create a new screenshot record
        
        Args:
            screenshot: Screenshot entity to create
            
        Returns:
            Created screenshot entity with any generated fields
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, screenshot_id: str) -> Optional[Screenshot]:
        """
        Get screenshot by ID
        
        Args:
            screenshot_id: Unique screenshot identifier
            
        Returns:
            Screenshot entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update(self, screenshot: Screenshot) -> Screenshot:
        """
        Update existing screenshot record
        
        Args:
            screenshot: Screenshot entity to update
            
        Returns:
            Updated screenshot entity
        """
        pass
    
    @abstractmethod
    async def delete(self, screenshot_id: str) -> bool:
        """
        Delete screenshot by ID
        
        Args:
            screenshot_id: Unique screenshot identifier
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_all(
        self, 
        limit: Optional[int] = None, 
        offset: int = 0
    ) -> List[Screenshot]:
        """
        List all screenshots with pagination
        
        Args:
            limit: Maximum number of screenshots to return
            offset: Number of screenshots to skip
            
        Returns:
            List of screenshot entities
        """
        pass
    
    @abstractmethod
    async def find_by_session(self, session_id: str) -> List[Screenshot]:
        """
        Find screenshots by monitoring session ID
        
        Args:
            session_id: Monitoring session identifier
            
        Returns:
            List of screenshots from the session
        """
        pass
    
    @abstractmethod
    async def find_by_roi(self, roi_id: str) -> List[Screenshot]:
        """
        Find screenshots by ROI region ID
        
        Args:
            roi_id: ROI region identifier
            
        Returns:
            List of screenshots from the ROI
        """
        pass
    
    @abstractmethod
    async def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Screenshot]:
        """
        Find screenshots within date range
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of screenshots in date range
        """
        pass
    
    @abstractmethod
    async def find_by_criteria(self, criteria: Dict[str, Any]) -> List[Screenshot]:
        """
        Find screenshots matching criteria
        
        Args:
            criteria: Dictionary of search criteria
            
        Returns:
            List of matching screenshots
        """
        pass
    
    @abstractmethod
    async def get_total_count(self) -> int:
        """
        Get total count of screenshots
        
        Returns:
            Total number of screenshots
        """
        pass
    
    @abstractmethod
    async def get_storage_size(self) -> int:
        """
        Get total storage size of all screenshots
        
        Returns:
            Total size in bytes
        """
        pass
    
    @abstractmethod
    async def cleanup_older_than(self, max_age_days: int) -> int:
        """
        Clean up screenshots older than specified days
        
        Args:
            max_age_days: Maximum age in days
            
        Returns:
            Number of screenshots deleted
        """
        pass
