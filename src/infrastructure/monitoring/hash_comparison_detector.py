"""
Hash comparison-based change detection strategy
"""
from typing import Dict, Any, Optional
import hashlib
from PIL import Image
import io
from ...domain.interfaces.change_detection_strategy import IChangeDetectionStrategy


class HashComparisonDetector(IChangeDetectionStrategy):
    """
    Change detection based on image hash comparison
    Fast and memory efficient for exact change detection
    """
    
    def __init__(self):
        self._baseline_hash: Optional[str] = None
        self._baseline_size: int = 0
        self._initialized: bool = False
        self._detection_count: int = 0
        self._hash_algorithm: str = 'md5'
    
    def initialize(self, baseline_image: bytes) -> bool:
        """Initialize with baseline image"""
        try:
            if not baseline_image:
                return False
            
            self._baseline_hash = self._calculate_hash(baseline_image)
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
        Detect changes by comparing image hashes
        
        Args:
            current_image: Current image data
            threshold: Not used for hash comparison (binary result)
            
        Returns:
            Dict with detection results
        """
        if not self._initialized or not self._baseline_hash:
            return {
                'has_changes': False,
                'change_score': 0.0,
                'error': 'Strategy not initialized',
                'metadata': {}
            }
        
        try:
            current_hash = self._calculate_hash(current_image)
            current_size = len(current_image)
            
            # Hash comparison is binary - either identical or different
            has_changes = current_hash != self._baseline_hash
            change_score = 100.0 if has_changes else 0.0
            
            self._detection_count += 1
            
            metadata = {
                'baseline_hash': self._baseline_hash,
                'current_hash': current_hash,
                'baseline_size': self._baseline_size,
                'current_size': current_size,
                'hash_algorithm': self._hash_algorithm,
                'detection_count': self._detection_count,
                'threshold_ignored': threshold  # Hash comparison ignores threshold
            }
            
            return {
                'has_changes': has_changes,
                'change_score': change_score,
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
            
            self._baseline_hash = self._calculate_hash(new_baseline)
            self._baseline_size = len(new_baseline)
            return True
        except Exception:
            return False
    
    def get_strategy_name(self) -> str:
        """Get strategy name"""
        return "hash_comparison_detector"
    
    def get_strategy_metadata(self) -> Dict[str, Any]:
        """Get strategy metadata"""
        return {
            'name': self.get_strategy_name(),
            'description': 'Hash-based exact change detection',
            'initialized': self._initialized,
            'baseline_hash': self._baseline_hash,
            'baseline_size': self._baseline_size,
            'hash_algorithm': self._hash_algorithm,
            'detection_count': self._detection_count,
            'fast': True,
            'accuracy': 'exact'
        }
    
    def reset(self) -> bool:
        """Reset strategy state"""
        try:
            self._baseline_hash = None
            self._baseline_size = 0
            self._initialized = False
            self._detection_count = 0
            return True
        except Exception:
            return False
    
    def _calculate_hash(self, image_data: bytes) -> str:
        """
        Calculate hash of image data
        
        Args:
            image_data: Image bytes to hash
            
        Returns:
            str: Hexadecimal hash string
        """
        if self._hash_algorithm == 'md5':
            return hashlib.md5(image_data).hexdigest()
        elif self._hash_algorithm == 'sha256':
            return hashlib.sha256(image_data).hexdigest()
        else:
            # Default to MD5
            return hashlib.md5(image_data).hexdigest()
    
    def set_hash_algorithm(self, algorithm: str) -> bool:
        """
        Set the hash algorithm to use
        
        Args:
            algorithm: 'md5' or 'sha256'
            
        Returns:
            bool: True if algorithm is supported
        """
        if algorithm in ['md5', 'sha256']:
            self._hash_algorithm = algorithm
            return True
        return False
