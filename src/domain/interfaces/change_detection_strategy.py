"""
Change detection strategy interface for monitoring layer
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from ..value_objects.timestamp import Timestamp


class IChangeDetectionStrategy(ABC):
    """Interface for change detection strategies"""
    
    @abstractmethod
    def initialize(self, baseline_image: bytes) -> bool:
        """
        Initialize the strategy with a baseline image
        
        Args:
            baseline_image: The initial image data to compare against
            
        Returns:
            bool: True if initialization successful
        """
        pass
    
    @abstractmethod
    def detect_changes(
        self, 
        current_image: bytes, 
        threshold: float = 20.0
    ) -> Dict[str, Any]:
        """
        Detect changes between baseline and current image
        
        Args:
            current_image: Current image data to analyze
            threshold: Sensitivity threshold for change detection (0-100)
            
        Returns:
            Dict containing:
                - has_changes: bool
                - change_score: float (0-100)
                - metadata: Dict with strategy-specific data
        """
        pass
    
    @abstractmethod
    def update_baseline(self, new_baseline: bytes) -> bool:
        """
        Update the baseline image for future comparisons
        
        Args:
            new_baseline: New baseline image data
            
        Returns:
            bool: True if update successful
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """
        Get the name of this detection strategy
        
        Returns:
            str: Strategy name
        """
        pass
    
    @abstractmethod
    def get_strategy_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this strategy's configuration
        
        Returns:
            Dict with strategy configuration and status
        """
        pass
    
    @abstractmethod
    def reset(self) -> bool:
        """
        Reset the strategy to initial state
        
        Returns:
            bool: True if reset successful
        """
        pass


class IChangeDetectionContext(ABC):
    """Context interface for managing change detection strategies"""
    
    @abstractmethod
    def set_strategy(self, strategy: IChangeDetectionStrategy) -> bool:
        """
        Set the active change detection strategy
        
        Args:
            strategy: The strategy to use for change detection
            
        Returns:
            bool: True if strategy set successfully
        """
        pass
    
    @abstractmethod
    def get_current_strategy(self) -> Optional[IChangeDetectionStrategy]:
        """
        Get the currently active strategy
        
        Returns:
            Optional[IChangeDetectionStrategy]: Current strategy or None
        """
        pass
    
    @abstractmethod
    def detect_changes(
        self, 
        current_image: bytes, 
        threshold: float = 20.0
    ) -> Dict[str, Any]:
        """
        Detect changes using the current strategy
        
        Args:
            current_image: Current image data to analyze
            threshold: Sensitivity threshold for change detection
            
        Returns:
            Dict with change detection results
        """
        pass
    
    @abstractmethod
    def initialize_baseline(self, baseline_image: bytes) -> bool:
        """
        Initialize baseline for current strategy
        
        Args:
            baseline_image: Baseline image data
            
        Returns:
            bool: True if initialization successful
        """
        pass
