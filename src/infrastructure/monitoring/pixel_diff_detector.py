"""
Pixel difference-based change detection strategy
"""
from typing import Dict, Any, Optional
from PIL import Image
import io
import numpy as np
from ...domain.interfaces.change_detection_strategy import IChangeDetectionStrategy


class PixelDiffDetector(IChangeDetectionStrategy):
    """
    Change detection based on pixel-by-pixel comparison
    More accurate but computationally intensive
    """
    
    def __init__(self):
        self._baseline_image: Optional[bytes] = None
        self._baseline_array: Optional[np.ndarray] = None
        self._initialized: bool = False
        self._detection_count: int = 0
        self._last_change_score: float = 0.0
    
    def initialize(self, baseline_image: bytes) -> bool:
        """Initialize with baseline image"""
        try:
            if not baseline_image:
                return False
            
            # Convert bytes to PIL Image and then to numpy array
            baseline_pil = Image.open(io.BytesIO(baseline_image))
            self._baseline_array = np.array(baseline_pil)
            self._baseline_image = baseline_image
            self._initialized = True
            self._detection_count = 0
            self._last_change_score = 0.0
            
            return True
        except Exception:
            return False
    
    def detect_changes(
        self, 
        current_image: bytes, 
        threshold: float = 20.0
    ) -> Dict[str, Any]:
        """
        Detect changes by comparing pixel differences
        
        Args:
            current_image: Current image data
            threshold: Pixel difference threshold percentage (0-100)
            
        Returns:
            Dict with detection results
        """
        if not self._initialized or self._baseline_array is None:
            return {
                'has_changes': False,
                'change_score': 0.0,
                'error': 'Strategy not initialized',
                'metadata': {}
            }
        
        try:
            # Convert current image to numpy array
            current_pil = Image.open(io.BytesIO(current_image))
            current_array = np.array(current_pil)
            
            # Ensure images have same dimensions
            if current_array.shape != self._baseline_array.shape:
                # Resize current image to match baseline
                baseline_pil = Image.fromarray(self._baseline_array)
                current_pil = current_pil.resize(baseline_pil.size)
                current_array = np.array(current_pil)
            
            # Calculate pixel differences
            diff_array = np.abs(current_array.astype(float) - self._baseline_array.astype(float))
            
            # Calculate percentage of changed pixels
            if len(diff_array.shape) == 3:  # Color image
                # Consider a pixel changed if any channel differs significantly
                pixel_changes = np.any(diff_array > 30, axis=2)  # 30 out of 255
            else:  # Grayscale
                pixel_changes = diff_array > 30
            
            total_pixels = pixel_changes.size
            changed_pixels = np.sum(pixel_changes)
            change_percentage = (changed_pixels / total_pixels) * 100.0
            
            has_changes = change_percentage >= threshold
            self._detection_count += 1
            self._last_change_score = change_percentage
            
            metadata = {
                'total_pixels': int(total_pixels),
                'changed_pixels': int(changed_pixels),
                'change_percentage': float(change_percentage),
                'threshold_used': threshold,
                'detection_count': self._detection_count,
                'image_shape': current_array.shape,
                'mean_pixel_diff': float(np.mean(diff_array))
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
            
            baseline_pil = Image.open(io.BytesIO(new_baseline))
            self._baseline_array = np.array(baseline_pil)
            self._baseline_image = new_baseline
            return True
        except Exception:
            return False
    
    def get_strategy_name(self) -> str:
        """Get strategy name"""
        return "pixel_diff_detector"
    
    def get_strategy_metadata(self) -> Dict[str, Any]:
        """Get strategy metadata"""
        baseline_shape = self._baseline_array.shape if self._baseline_array is not None else None
        
        return {
            'name': self.get_strategy_name(),
            'description': 'Pixel-by-pixel difference analysis',
            'initialized': self._initialized,
            'baseline_shape': baseline_shape,
            'detection_count': self._detection_count,
            'last_change_score': self._last_change_score,
            'fast': False,
            'accuracy': 'high'
        }
    
    def reset(self) -> bool:
        """Reset strategy state"""
        try:
            self._baseline_image = None
            self._baseline_array = None
            self._initialized = False
            self._detection_count = 0
            self._last_change_score = 0.0
            return True
        except Exception:
            return False
