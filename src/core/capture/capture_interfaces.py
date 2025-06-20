"""
Abstract base classes and interfaces for screenshot capture
Part of Phase 1.2 - Screenshot Capture Module Refactoring
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class CaptureResult:
    """Result of a screenshot capture operation with error handling"""
    
    def __init__(self, success: bool, data: Optional[bytes] = None, 
                 error: Optional[str] = None, metadata: Optional[dict] = None):
        self.success = success
        self.data = data
        self.error = error
        self.metadata = metadata or {}
    
    @property
    def size(self) -> int:
        """Size of captured data in bytes"""
        return len(self.data) if self.data else 0
    
    def __bool__(self) -> bool:
        """Boolean evaluation returns success status"""
        return self.success


class CaptureMethod(Enum):
    """Available screenshot capture methods"""
    WSL_POWERSHELL = "wsl_powershell"
    WINDOWS_NATIVE = "windows_native"
    MSS = "mss"
    PYAUTOGUI = "pyautogui"
    HEADLESS = "headless"


@dataclass
class CaptureCapabilities:
    """Capabilities of a capture method"""
    supports_roi: bool = True
    supports_multi_monitor: bool = True
    requires_elevated: bool = False
    max_capture_size: Optional[Tuple[int, int]] = None
    performance_rating: int = 1  # 1-5, higher is better


class AbstractScreenshotCapture(ABC):
    """Abstract base class for all screenshot capture implementations"""
    
    def __init__(self, config):
        self.config = config
        self._initialized = False
        self._capabilities = CaptureCapabilities()
    
    @property
    def capabilities(self) -> CaptureCapabilities:
        """Get capabilities of this capture method"""
        return self._capabilities
    
    @property
    def is_initialized(self) -> bool:
        """Check if capture method is initialized"""
        return self._initialized
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the capture method"""
        pass
    
    @abstractmethod
    def capture_full_screen(self) -> CaptureResult:
        """Capture full screen screenshot"""
        pass
    
    @abstractmethod
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture a specific region of interest"""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources"""
        pass
    
    def validate_roi(self, roi: Tuple[int, int, int, int]) -> bool:
        """Validate ROI coordinates"""
        left, top, right, bottom = roi
        
        # Basic validation
        if left >= right or top >= bottom:
            return False
        
        # Check minimum size
        min_width = self.config.get('min_roi_width', 50)
        min_height = self.config.get('min_roi_height', 50)
        
        if (right - left) < min_width or (bottom - top) < min_height:
            return False
        
        return True


class ScreenshotCaptureFactory:
    """Factory for creating appropriate screenshot capture instances"""
    
    @staticmethod
    def create_capture(method: CaptureMethod, config) -> AbstractScreenshotCapture:
        """Create a screenshot capture instance for the specified method"""
        from .capture_implementations import (
            WSLPowerShellCapture,
            WindowsNativeCapture,
            MSSCapture,
            PyAutoGUICapture,
            HeadlessCapture
        )
        
        capture_classes = {
            CaptureMethod.WSL_POWERSHELL: WSLPowerShellCapture,
            CaptureMethod.WINDOWS_NATIVE: WindowsNativeCapture,
            CaptureMethod.MSS: MSSCapture,
            CaptureMethod.PYAUTOGUI: PyAutoGUICapture,
            CaptureMethod.HEADLESS: HeadlessCapture,
        }
        
        capture_class = capture_classes.get(method)
        if not capture_class:
            raise ValueError(f"Unsupported capture method: {method}")
        
        return capture_class(config)
    
    @staticmethod
    def get_recommended_method() -> CaptureMethod:
        """Get the recommended capture method for current platform"""
        from .platform_detection import get_recommended_screenshot_method
        
        method_mapping = {
            'wsl_powershell': CaptureMethod.WSL_POWERSHELL,
            'windows_native': CaptureMethod.WINDOWS_NATIVE,
            'mss': CaptureMethod.MSS,
            'pyautogui': CaptureMethod.PYAUTOGUI,
            'headless': CaptureMethod.HEADLESS,
        }
        
        recommended = get_recommended_screenshot_method()
        return method_mapping.get(recommended, CaptureMethod.PYAUTOGUI)
