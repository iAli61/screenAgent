"""
Refactored screenshot capture module for ScreenAgent
Uses modular architecture with abstract interfaces and platform-specific implementations
Part of Phase 1.2 - Screenshot Capture Module Refactoring
"""
import os
from typing import Optional, Tuple, List
from .capture_interfaces import (
    AbstractScreenshotCapture, 
    CaptureResult, 
    CaptureMethod, 
    ScreenshotCaptureFactory
)
from ..config import Config


class ScreenshotCaptureManager:
    """
    High-level manager for screenshot capture operations
    Provides a clean interface and handles fallback strategies
    """
    
    def __init__(self, config: Config):
        self.config = config
        self._primary_capture: Optional[AbstractScreenshotCapture] = None
        self._fallback_captures: List[AbstractScreenshotCapture] = []
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize capture manager with primary and fallback methods"""
        try:
            # Get recommended method for platform
            primary_method = ScreenshotCaptureFactory.get_recommended_method()
            
            # Create primary capture instance
            self._primary_capture = ScreenshotCaptureFactory.create_capture(primary_method, self.config)
            
            # Initialize primary method
            if not self._primary_capture.initialize():
                print(f"❌ Failed to initialize primary capture method: {primary_method.value}")
                self._primary_capture = None
            else:
                print(f"✅ Primary capture method initialized: {primary_method.value}")
            
            # Setup fallback methods
            self._setup_fallback_methods(primary_method)
            
            # Mark as initialized if we have at least one working method
            self._initialized = bool(self._primary_capture or self._fallback_captures)
            
            if not self._initialized:
                print("❌ No screenshot capture methods available")
                return False
            
            print(f"✅ Screenshot capture manager initialized with {len(self._fallback_captures)} fallback methods")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize screenshot capture manager: {e}")
            return False
    
    def _setup_fallback_methods(self, primary_method: CaptureMethod) -> None:
        """Setup fallback capture methods"""
        # Define fallback order based on reliability and availability
        fallback_order = [
            CaptureMethod.PYAUTOGUI,
            CaptureMethod.WINDOWS_NATIVE,
            CaptureMethod.MSS,
            CaptureMethod.WSL_POWERSHELL,
        ]
        
        # Remove primary method from fallbacks
        fallback_order = [method for method in fallback_order if method != primary_method]
        
        for method in fallback_order:
            try:
                capture = ScreenshotCaptureFactory.create_capture(method, self.config)
                if capture.initialize():
                    self._fallback_captures.append(capture)
                    print(f"✅ Fallback capture method available: {method.value}")
            except Exception as e:
                print(f"⚠️  Fallback method {method.value} unavailable: {e}")
    
    def capture_full_screen(self) -> CaptureResult:
        """Capture full screen with automatic fallback"""
        if not self._initialized:
            return CaptureResult(False, error="Capture manager not initialized")
        
        # Try primary method first
        if self._primary_capture:
            result = self._primary_capture.capture_full_screen()
            if result.success:
                return result
            else:
                print(f"⚠️  Primary capture failed: {result.error}")
        
        # Try fallback methods
        for capture in self._fallback_captures:
            try:
                result = capture.capture_full_screen()
                if result.success:
                    print(f"✅ Fallback capture successful: {capture.__class__.__name__}")
                    return result
            except Exception as e:
                print(f"⚠️  Fallback capture failed: {e}")
        
        return CaptureResult(False, error="All capture methods failed")
    
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture region of interest with automatic fallback"""
        if not self._initialized:
            return CaptureResult(False, error="Capture manager not initialized")
        
        # Try primary method first
        if self._primary_capture:
            result = self._primary_capture.capture_roi(roi)
            if result.success:
                return result
            else:
                print(f"⚠️  Primary ROI capture failed: {result.error}")
        
        # Try fallback methods
        for capture in self._fallback_captures:
            try:
                result = capture.capture_roi(roi)
                if result.success:
                    print(f"✅ Fallback ROI capture successful: {capture.__class__.__name__}")
                    return result
            except Exception as e:
                print(f"⚠️  Fallback ROI capture failed: {e}")
        
        return CaptureResult(False, error="All ROI capture methods failed")
    
    def get_capabilities(self) -> dict:
        """Get capabilities of available capture methods"""
        capabilities = {
            'primary': None,
            'fallbacks': [],
            'summary': {
                'supports_roi': False,
                'supports_multi_monitor': False,
                'best_performance_rating': 0
            }
        }
        
        if self._primary_capture:
            capabilities['primary'] = {
                'method': self._primary_capture.__class__.__name__,
                'capabilities': self._primary_capture.capabilities.__dict__
            }
            capabilities['summary']['supports_roi'] = self._primary_capture.capabilities.supports_roi
            capabilities['summary']['supports_multi_monitor'] = self._primary_capture.capabilities.supports_multi_monitor
            capabilities['summary']['best_performance_rating'] = self._primary_capture.capabilities.performance_rating
        
        for capture in self._fallback_captures:
            fallback_info = {
                'method': capture.__class__.__name__,
                'capabilities': capture.capabilities.__dict__
            }
            capabilities['fallbacks'].append(fallback_info)
            
            # Update summary with best available capabilities
            if capture.capabilities.supports_roi:
                capabilities['summary']['supports_roi'] = True
            if capture.capabilities.supports_multi_monitor:
                capabilities['summary']['supports_multi_monitor'] = True
            if capture.capabilities.performance_rating > capabilities['summary']['best_performance_rating']:
                capabilities['summary']['best_performance_rating'] = capture.capabilities.performance_rating
        
        return capabilities
    
    def cleanup(self) -> None:
        """Clean up all capture resources"""
        if self._primary_capture:
            self._primary_capture.cleanup()
            self._primary_capture = None
        
        for capture in self._fallback_captures:
            capture.cleanup()
        
        self._fallback_captures.clear()
        self._initialized = False
    
    def __del__(self):
        """Ensure cleanup on destruction"""
        self.cleanup()


# Backward compatibility wrapper for the old ScreenshotCapture class
class ScreenshotCapture:
    """Backward compatibility wrapper for the old ScreenshotCapture interface"""
    
    def __init__(self, config: Config):
        self._manager = ScreenshotCaptureManager(config)
        self.config = config
        self.method = None  # For backward compatibility
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize screenshot capture"""
        success = self._manager.initialize()
        if success:
            self._initialized = True
            # Set method for backward compatibility
            capabilities = self._manager.get_capabilities()
            if capabilities['primary']:
                self.method = capabilities['primary']['method'].lower().replace('capture', '').replace('_', '')
        return success
    
    def capture_full_screen(self) -> Optional[bytes]:
        """Capture full screen - backward compatible interface"""
        result = self._manager.capture_full_screen()
        return result.data if result.success else None
    
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> Optional[bytes]:
        """Capture ROI - backward compatible interface"""
        result = self._manager.capture_roi(roi)
        return result.data if result.success else None


# Legacy functions for backward compatibility
def take_screenshot(roi: Tuple[int, int, int, int] = None) -> Optional[bytes]:
    """Legacy function for taking screenshots"""
    config = Config()
    manager = ScreenshotCaptureManager(config)
    
    if not manager.initialize():
        return None
    
    try:
        if roi:
            result = manager.capture_roi(roi)
        else:
            result = manager.capture_full_screen()
        
        return result.data if result.success else None
    finally:
        manager.cleanup()


def take_full_screenshot(save_to_temp: bool = False) -> Optional[bytes]:
    """Legacy function for taking full screenshots"""
    config = Config()
    manager = ScreenshotCaptureManager(config)
    
    if not manager.initialize():
        return None
    
    try:
        result = manager.capture_full_screen()
        
        if result.success and save_to_temp:
            try:
                temp_path = config.temp_screenshot_path
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                with open(temp_path, 'wb') as f:
                    f.write(result.data)
            except Exception as e:
                print(f"❌ Failed to save temp screenshot: {e}")
        
        return result.data if result.success else None
    finally:
        manager.cleanup()
