"""
Capture chain builder implementing chain of responsibility pattern
Builds and manages the chain of capture handlers
"""
from typing import List, Optional, Tuple, Dict, Any

from . import ICaptureChain, ICaptureHandler, CaptureMethod, CaptureResult
from .platform_detector import PlatformDetector
from .windows_capture import WindowsNativeCapture, WindowsMSSCapture
from .linux_capture import LinuxX11Capture, LinuxWaylandCapture
from .wsl_capture import WSLPowerShellCapture, WSLPyAutoGUICapture


class CaptureChainBuilder(ICaptureChain):
    """Builds capture handler chain based on platform and availability"""
    
    def __init__(self):
        self.platform_detector = PlatformDetector()
        self._chain_cache: Optional[ICaptureHandler] = None
    
    def build_chain(self) -> ICaptureHandler:
        """Build and return the capture chain for current platform"""
        if self._chain_cache is not None:
            return self._chain_cache
        
        # Get recommended methods for current platform
        recommended_methods = self.platform_detector.get_recommended_methods()
        print(f"Recommended capture methods: {[m.value for m in recommended_methods]}")
        
        # Create handlers for available methods
        handlers = self._create_handlers(recommended_methods)
        
        # Filter to only handlers that can handle current platform
        available_handlers = [h for h in handlers if h.can_handle()]
        
        if not available_handlers:
            raise RuntimeError("No capture handlers available for current platform")
        
        # Initialize handlers
        initialized_handlers = []
        for handler in available_handlers:
            try:
                if handler.initialize():
                    initialized_handlers.append(handler)
                    print(f"✅ Initialized capture handler: {handler.capabilities.method.value}")
                else:
                    print(f"⚠️  Failed to initialize handler: {handler.capabilities.method.value}")
            except Exception as e:
                print(f"❌ Error initializing handler {handler.capabilities.method.value}: {e}")
        
        if not initialized_handlers:
            raise RuntimeError("No capture handlers could be initialized")
        
        # Build chain of responsibility
        chain_head = initialized_handlers[0]
        current = chain_head
        
        for handler in initialized_handlers[1:]:
            current.set_next(handler)
            current = handler
        
        self._chain_cache = chain_head
        print(f"✅ Built capture chain with {len(initialized_handlers)} handlers")
        
        return chain_head
    
    def _create_handlers(self, methods: List[CaptureMethod]) -> List[ICaptureHandler]:
        """Create handler instances for the given methods"""
        handlers = []
        
        for method in methods:
            handler = self._create_handler(method)
            if handler:
                handlers.append(handler)
        
        return handlers
    
    def _create_handler(self, method: CaptureMethod) -> Optional[ICaptureHandler]:
        """Create a handler for the given capture method"""
        try:
            print(f"Creating handler for: {method.value}")
            
            if method == CaptureMethod.WINDOWS_NATIVE:
                return WindowsNativeCapture()
            elif method == CaptureMethod.MSS:
                return WindowsMSSCapture()
            elif method == CaptureMethod.LINUX_X11:
                return LinuxX11Capture()
            elif method == CaptureMethod.LINUX_WAYLAND:
                return LinuxWaylandCapture()
            elif method == CaptureMethod.WSL_POWERSHELL:
                return WSLPowerShellCapture()
            elif method == CaptureMethod.PYAUTOGUI:
                return WSLPyAutoGUICapture()  # Can be used on any platform
            else:
                print(f"⚠️  Unknown capture method: {method}")
                return None
        except Exception as e:
            print(f"❌ Failed to create handler for {method}: {e}")
            return None
    
    def get_available_methods(self) -> List[CaptureMethod]:
        """Get list of available capture methods on current platform"""
        return self.platform_detector.get_recommended_methods()
    
    def rebuild_chain(self) -> ICaptureHandler:
        """Rebuild the capture chain (clears cache)"""
        if self._chain_cache:
            self._cleanup_chain(self._chain_cache)
        
        self._chain_cache = None
        self.platform_detector.clear_cache()
        
        return self.build_chain()
    
    def _cleanup_chain(self, head: ICaptureHandler) -> None:
        """Clean up all handlers in the chain"""
        current = head
        while current:
            try:
                current.cleanup()
            except Exception as e:
                print(f"⚠️  Error cleaning up handler: {e}")
            current = current._next_handler
    
    def get_chain_info(self) -> dict:
        """Get information about the current capture chain"""
        if not self._chain_cache:
            return {'status': 'not_built', 'handlers': []}
        
        handlers_info = []
        current = self._chain_cache
        position = 0
        
        while current:
            handler_info = {
                'position': position,
                'method': current.capabilities.method.value if current.capabilities else 'unknown',
                'initialized': current.is_initialized,
                'capabilities': current.capabilities.__dict__ if current.capabilities else {}
            }
            handlers_info.append(handler_info)
            current = current._next_handler
            position += 1
        
        return {
            'status': 'built',
            'handlers': handlers_info,
            'platform_info': self.platform_detector.get_display_info()
        }

    # Add compatibility methods for the CaptureServiceImpl class
    def capture_full_screen(self) -> CaptureResult:
        """Compatibility method for CaptureServiceImpl"""
        if not self._chain_cache:
            return CaptureResult(False, error="Capture chain not initialized")
        return self._chain_cache.handle_full_screen()
    
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Compatibility method for CaptureServiceImpl"""
        if not self._chain_cache:
            return CaptureResult(False, error="Capture chain not initialized")
        return self._chain_cache.handle_roi(roi)
    
    def cleanup(self) -> None:
        """Clean up the capture chain"""
        if self._chain_cache:
            self._cleanup_chain(self._chain_cache)
            self._chain_cache = None
