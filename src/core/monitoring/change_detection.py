"""
Change detection interfaces and strategies for ROI monitoring
Part of Phase 1.3 - ROI Monitor Module Refactoring
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import hashlib
import time


class ChangeDetectionMethod(Enum):
    """Available change detection methods"""
    SIZE_BASED = "size_based"
    HASH_BASED = "hash_based"
    PIXEL_DIFF = "pixel_diff"
    ADVANCED_DIFF = "advanced_diff"


@dataclass
class ChangeDetectionResult:
    """Result of change detection analysis"""
    changed: bool
    confidence: float  # 0.0 to 1.0
    change_score: float  # Magnitude of change
    method: str
    metadata: Dict[str, Any]
    processing_time: float


@dataclass
class ChangeEvent:
    """Event data for when changes are detected"""
    timestamp: float
    screenshot_data: bytes
    roi: tuple
    change_result: ChangeDetectionResult
    screenshot_id: str


class AbstractChangeDetector(ABC):
    """Abstract base class for change detection algorithms"""
    
    def __init__(self, config, sensitivity: float = 0.5):
        self.config = config
        self.sensitivity = sensitivity  # 0.0 (least sensitive) to 1.0 (most sensitive)
        self._baseline_data: Optional[bytes] = None
        self._baseline_metadata: Dict[str, Any] = {}
    
    @property
    @abstractmethod
    def method_name(self) -> str:
        """Get the name of this detection method"""
        pass
    
    @property
    @abstractmethod
    def supports_roi_analysis(self) -> bool:
        """Whether this method can analyze specific ROI regions"""
        pass
    
    @abstractmethod
    def detect_change(self, current_data: bytes, roi: tuple) -> ChangeDetectionResult:
        """Detect changes between baseline and current data"""
        pass
    
    def set_baseline(self, data: bytes, metadata: Dict[str, Any] = None) -> None:
        """Set the baseline for change detection"""
        self._baseline_data = data
        self._baseline_metadata = metadata or {}
    
    def has_baseline(self) -> bool:
        """Check if baseline is set"""
        return self._baseline_data is not None
    
    def reset_baseline(self) -> None:
        """Reset the baseline"""
        self._baseline_data = None
        self._baseline_metadata = {}
    
    def update_sensitivity(self, sensitivity: float) -> None:
        """Update sensitivity (0.0 to 1.0)"""
        self.sensitivity = max(0.0, min(1.0, sensitivity))


class SizeBasedChangeDetector(AbstractChangeDetector):
    """Simple change detection based on data size differences"""
    
    @property
    def method_name(self) -> str:
        return "size_based"
    
    @property
    def supports_roi_analysis(self) -> bool:
        return False
    
    def detect_change(self, current_data: bytes, roi: tuple) -> ChangeDetectionResult:
        """Detect changes based on size differences"""
        start_time = time.time()
        
        if not self.has_baseline():
            # First screenshot - no change detected
            result = ChangeDetectionResult(
                changed=False,
                confidence=1.0,
                change_score=0.0,
                method=self.method_name,
                metadata={'baseline_size': len(current_data)},
                processing_time=time.time() - start_time
            )
            self.set_baseline(current_data)
            return result
        
        baseline_size = len(self._baseline_data)
        current_size = len(current_data)
        
        # Calculate size difference percentage
        size_diff_pct = abs(current_size - baseline_size) / baseline_size if baseline_size > 0 else 1.0
        
        # Sensitivity threshold: higher sensitivity means smaller changes trigger detection
        threshold = (1.0 - self.sensitivity) * 0.1  # 0% to 10% change threshold
        
        changed = size_diff_pct > threshold
        confidence = min(1.0, size_diff_pct / threshold) if threshold > 0 else 1.0
        
        return ChangeDetectionResult(
            changed=changed,
            confidence=confidence,
            change_score=size_diff_pct,
            method=self.method_name,
            metadata={
                'baseline_size': baseline_size,
                'current_size': current_size,
                'size_diff_pct': size_diff_pct,
                'threshold': threshold
            },
            processing_time=time.time() - start_time
        )


class HashBasedChangeDetector(AbstractChangeDetector):
    """Change detection based on hash comparison"""
    
    @property
    def method_name(self) -> str:
        return "hash_based"
    
    @property
    def supports_roi_analysis(self) -> bool:
        return False
    
    def detect_change(self, current_data: bytes, roi: tuple) -> ChangeDetectionResult:
        """Detect changes based on hash comparison"""
        start_time = time.time()
        
        current_hash = hashlib.md5(current_data).hexdigest()
        
        if not self.has_baseline():
            # First screenshot - no change detected
            result = ChangeDetectionResult(
                changed=False,
                confidence=1.0,
                change_score=0.0,
                method=self.method_name,
                metadata={'baseline_hash': current_hash},
                processing_time=time.time() - start_time
            )
            self.set_baseline(current_data, {'hash': current_hash})
            return result
        
        baseline_hash = self._baseline_metadata.get('hash')
        if not baseline_hash:
            # Recalculate baseline hash if missing
            baseline_hash = hashlib.md5(self._baseline_data).hexdigest()
            self._baseline_metadata['hash'] = baseline_hash
        
        changed = current_hash != baseline_hash
        confidence = 1.0 if changed else 1.0  # Hash is binary - either same or different
        change_score = 1.0 if changed else 0.0
        
        return ChangeDetectionResult(
            changed=changed,
            confidence=confidence,
            change_score=change_score,
            method=self.method_name,
            metadata={
                'baseline_hash': baseline_hash,
                'current_hash': current_hash,
                'hash_match': not changed
            },
            processing_time=time.time() - start_time
        )


class PixelDiffChangeDetector(AbstractChangeDetector):
    """Change detection based on pixel-level differences (requires PIL)"""
    
    def __init__(self, config, sensitivity: float = 0.5):
        super().__init__(config, sensitivity)
        self._pil_available = self._check_pil_availability()
    
    def _check_pil_availability(self) -> bool:
        """Check if PIL is available for image processing"""
        try:
            from PIL import Image
            import numpy as np
            return True
        except ImportError:
            return False
    
    @property
    def method_name(self) -> str:
        return "pixel_diff"
    
    @property
    def supports_roi_analysis(self) -> bool:
        return True
    
    def detect_change(self, current_data: bytes, roi: tuple) -> ChangeDetectionResult:
        """Detect changes based on pixel differences"""
        start_time = time.time()
        
        if not self._pil_available:
            # Fallback to hash-based detection
            fallback_detector = HashBasedChangeDetector(self.config, self.sensitivity)
            if self.has_baseline():
                fallback_detector.set_baseline(self._baseline_data, self._baseline_metadata)
            result = fallback_detector.detect_change(current_data, roi)
            result.metadata['fallback_reason'] = 'PIL not available'
            return result
        
        try:
            from PIL import Image
            import numpy as np
            import io
            
            current_image = Image.open(io.BytesIO(current_data))
            current_array = np.array(current_image)
            
            if not self.has_baseline():
                # First screenshot - no change detected
                result = ChangeDetectionResult(
                    changed=False,
                    confidence=1.0,
                    change_score=0.0,
                    method=self.method_name,
                    metadata={'baseline_shape': current_array.shape},
                    processing_time=time.time() - start_time
                )
                self.set_baseline(current_data, {'array_shape': current_array.shape})
                return result
            
            baseline_image = Image.open(io.BytesIO(self._baseline_data))
            baseline_array = np.array(baseline_image)
            
            # Ensure images are the same size
            if current_array.shape != baseline_array.shape:
                # Size change is definitely a change
                return ChangeDetectionResult(
                    changed=True,
                    confidence=1.0,
                    change_score=1.0,
                    method=self.method_name,
                    metadata={
                        'baseline_shape': baseline_array.shape,
                        'current_shape': current_array.shape,
                        'reason': 'shape_mismatch'
                    },
                    processing_time=time.time() - start_time
                )
            
            # Calculate pixel differences
            diff = np.abs(current_array.astype(float) - baseline_array.astype(float))
            mean_diff = np.mean(diff)
            max_diff = np.max(diff)
            changed_pixels = np.sum(diff > 0)
            total_pixels = diff.size
            changed_pixel_ratio = changed_pixels / total_pixels
            
            # Sensitivity threshold: higher sensitivity means smaller changes trigger detection
            threshold = (1.0 - self.sensitivity) * 50.0  # 0 to 50 mean difference threshold
            
            changed = mean_diff > threshold
            confidence = min(1.0, mean_diff / threshold) if threshold > 0 else 1.0
            
            return ChangeDetectionResult(
                changed=changed,
                confidence=confidence,
                change_score=mean_diff / 255.0,  # Normalize to 0-1
                method=self.method_name,
                metadata={
                    'mean_diff': mean_diff,
                    'max_diff': max_diff,
                    'changed_pixels': changed_pixels,
                    'total_pixels': total_pixels,
                    'changed_pixel_ratio': changed_pixel_ratio,
                    'threshold': threshold
                },
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            # Fallback to hash-based detection on error
            fallback_detector = HashBasedChangeDetector(self.config, self.sensitivity)
            if self.has_baseline():
                fallback_detector.set_baseline(self._baseline_data, self._baseline_metadata)
            result = fallback_detector.detect_change(current_data, roi)
            result.metadata['fallback_reason'] = f'Pixel diff error: {e}'
            return result


class ChangeDetectorFactory:
    """Factory for creating change detection instances"""
    
    @staticmethod
    def create_detector(method: ChangeDetectionMethod, config, sensitivity: float = 0.5) -> AbstractChangeDetector:
        """Create a change detector instance"""
        detector_classes = {
            ChangeDetectionMethod.SIZE_BASED: SizeBasedChangeDetector,
            ChangeDetectionMethod.HASH_BASED: HashBasedChangeDetector,
            ChangeDetectionMethod.PIXEL_DIFF: PixelDiffChangeDetector,
            ChangeDetectionMethod.ADVANCED_DIFF: PixelDiffChangeDetector,  # Use pixel diff for now
        }
        
        detector_class = detector_classes.get(method)
        if not detector_class:
            raise ValueError(f"Unsupported change detection method: {method}")
        
        return detector_class(config, sensitivity)
    
    @staticmethod
    def get_recommended_method() -> ChangeDetectionMethod:
        """Get the recommended change detection method"""
        # Try to determine best method based on available libraries
        try:
            from PIL import Image
            import numpy as np
            return ChangeDetectionMethod.PIXEL_DIFF
        except ImportError:
            return ChangeDetectionMethod.HASH_BASED
    
    @staticmethod
    def get_available_methods() -> List[ChangeDetectionMethod]:
        """Get list of available change detection methods"""
        methods = [
            ChangeDetectionMethod.SIZE_BASED,
            ChangeDetectionMethod.HASH_BASED,
        ]
        
        # Check if PIL is available for advanced methods
        try:
            from PIL import Image
            import numpy as np
            methods.extend([
                ChangeDetectionMethod.PIXEL_DIFF,
                ChangeDetectionMethod.ADVANCED_DIFF,
            ])
        except ImportError:
            pass
        
        return methods
