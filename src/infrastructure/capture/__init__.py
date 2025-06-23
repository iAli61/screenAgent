"""
Infrastructure layer capture interfaces and base classes
Provides platform-agnostic interfaces for screenshot capture
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class CaptureResult:
    """Result of a screenshot capture operation"""
    
    def __init__(self, success: bool, data: Optional[bytes] = None, 
                 error: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
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
    WINDOWS_NATIVE = "windows_native"
    LINUX_X11 = "linux_x11"
    LINUX_WAYLAND = "linux_wayland"
    WSL_POWERSHELL = "wsl_powershell"
    MSS = "mss"
    PYAUTOGUI = "pyautogui"


@dataclass
class CaptureCapabilities:
    """Capabilities of a capture method"""
    method: CaptureMethod
    supports_roi: bool = True
    supports_multi_monitor: bool = True
    requires_elevated: bool = False
    max_capture_size: Optional[Tuple[int, int]] = None
    performance_rating: int = 1  # 1-5, higher is better
    reliability_rating: int = 1  # 1-5, higher is better
    platform_specific: bool = True


class ICaptureHandler(ABC):
    """Interface for capture handlers in the chain of responsibility"""
    
    def __init__(self):
        self._next_handler: Optional['ICaptureHandler'] = None
        self._capabilities: Optional[CaptureCapabilities] = None
        self._initialized = False
    
    @property
    def capabilities(self) -> Optional[CaptureCapabilities]:
        """Get capabilities of this capture handler"""
        return self._capabilities
    
    @property
    def is_initialized(self) -> bool:
        """Check if handler is initialized"""
        return self._initialized
    
    def set_next(self, handler: 'ICaptureHandler') -> 'ICaptureHandler':
        """Set the next handler in the chain"""
        self._next_handler = handler
        return handler
    
    @abstractmethod
    def can_handle(self) -> bool:
        """Check if this handler can handle capture on current platform"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the capture handler"""
        pass
    
    def handle_full_screen(self) -> CaptureResult:
        """Handle full screen capture request"""
        if self.can_handle() and self._initialized:
            result = self._capture_full_screen()
            if result.success:
                return result
        
        # Try next handler in chain
        if self._next_handler:
            return self._next_handler.handle_full_screen()
        
        return CaptureResult(False, error="No capture handler available")
    
    def handle_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Handle ROI capture request"""
        if self.can_handle() and self._initialized:
            if self._validate_roi(roi):
                result = self._capture_roi(roi)
                if result.success:
                    return result
        
        # Try next handler in chain
        if self._next_handler:
            return self._next_handler.handle_roi(roi)
        
        return CaptureResult(False, error="No ROI capture handler available")
    
    @abstractmethod
    def _capture_full_screen(self) -> CaptureResult:
        """Implement platform-specific full screen capture"""
        pass
    
    @abstractmethod
    def _capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Implement platform-specific ROI capture"""
        pass
    
    def _validate_roi(self, roi: Tuple[int, int, int, int]) -> bool:
        """Validate ROI coordinates"""
        left, top, right, bottom = roi
        
        # Basic validation
        if left >= right or top >= bottom:
            return False
        
        # Check minimum size (default 10x10 pixels)
        if (right - left) < 10 or (bottom - top) < 10:
            return False
        
        return True
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources"""
        pass


class ICaptureChain(ABC):
    """Interface for managing the capture chain"""
    
    @abstractmethod
    def build_chain(self) -> ICaptureHandler:
        """Build and return the capture chain"""
        pass
    
    @abstractmethod
    def get_available_methods(self) -> List[CaptureMethod]:
        """Get list of available capture methods on current platform"""
        pass


class IPlatformDetector(ABC):
    """Interface for platform detection"""
    
    @abstractmethod
    def is_windows(self) -> bool:
        """Check if running on Windows"""
        pass
    
    @abstractmethod
    def is_linux(self) -> bool:
        """Check if running on Linux"""
        pass
    
    @abstractmethod
    def is_wsl(self) -> bool:
        """Check if running in WSL"""
        pass
    
    @abstractmethod
    def is_wayland(self) -> bool:
        """Check if running on Wayland"""
        pass
    
    @abstractmethod
    def get_display_info(self) -> Dict[str, Any]:
        """Get display information"""
        pass


# Import and re-export main components
from .capture_chain import CaptureChainBuilder
from .platform_detector import PlatformDetector

__all__ = [
    'CaptureResult',
    'CaptureMethod', 
    'CaptureCapabilities',
    'ICaptureHandler',
    'ICaptureChain',
    'IPlatformDetector',
    'CaptureChainBuilder',
    'PlatformDetector'
]
