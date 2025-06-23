"""
Simple threshold-based change detection strategy
"""
from typing import Dict, Any, Optional
from ...domain.interfaces.change_detection_strategy import IChangeDetectionStrategy


class ThresholdDetector(IChangeDetectionStrategy):
    """
    Simple change detection based on image size threshold
    Fast but basic detection method
    """
    
    def __init__(self):
        self._baseline_image: Optional[bytes] = None
        self._baseline_size: int = 0
        self._initialized: bool = False
        self._detection_count: int = 0
    
    def initialize(self, baseline_image: bytes) -> bool:
        """Initialize with baseline image"""
        try:
            if not baseline_image:
                return False
            
            self._baseline_image = baseline_image
            self._baseline_size = len(baseline_image)
            self._initialized = True
            self._detection_count = 0
            
            return True
        except Exception:
            return False
    
    def detect_changes(
        self, 
        current_image: bytes, 
        threshold: float = 20.0
    ) -> Dict[str, Any]:
        """
        Detect changes by comparing image sizes
        
        Args:
            current_image: Current image data
            threshold: Size difference threshold percentage (0-100)
            
        Returns:
            Dict with detection results
        """
        if not self._initialized or not self._baseline_image:
            return {
                'has_changes': False,
                'change_score': 0.0,
                'error': 'Strategy not initialized',
                'metadata': {}
            }
        
        try:
            current_size = len(current_image)
            
            # Calculate percentage difference
            if self._baseline_size == 0:
                change_percentage = 100.0 if current_size > 0 else 0.0
            else:
                size_diff = abs(current_size - self._baseline_size)
                change_percentage = (size_diff / self._baseline_size) * 100.0
            
            has_changes = change_percentage >= threshold
            self._detection_count += 1
            
            metadata = {
                'baseline_size': self._baseline_size,
                'current_size': current_size,
                'size_difference': current_size - self._baseline_size,
                'threshold_used': threshold,
                'detection_count': self._detection_count
            }
            
            return {
                'has_changes': has_changes,
                'change_score': min(change_percentage, 100.0),
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'has_changes': False,
                'change_score': 0.0,
                'error': str(e),
                'metadata': {}
            }
    
    def update_baseline(self, new_baseline: bytes) -> bool:
        """Update baseline image"""
        try:
            if not new_baseline:
                return False
            
            self._baseline_image = new_baseline
            self._baseline_size = len(new_baseline)
            return True
        except Exception:
            return False
    
    def get_strategy_name(self) -> str:
        """Get strategy name"""
        return "threshold_detector"
    
    def get_strategy_metadata(self) -> Dict[str, Any]:
        """Get strategy metadata"""
        return {
            'name': self.get_strategy_name(),
            'description': 'Simple size-based change detection',
            'initialized': self._initialized,
            'baseline_size': self._baseline_size,
            'detection_count': self._detection_count,
            'fast': True,
            'accuracy': 'basic'
        }
    
    def reset(self) -> bool:
        """Reset strategy state"""
        try:
            self._baseline_image = None
            self._baseline_size = 0
            self._initialized = False
            self._detection_count = 0
            return True
        except Exception:
            return False
