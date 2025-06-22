"""
Unified Screenshot Manager for ScreenAgent
Consolidates all screenshot functionality into a single, clean interface
Removes duplication and simplifies the architecture
"""
import io
import os
import base64
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime

try:
    from PIL import Image
    import numpy as np
    PIL_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    NUMPY_AVAILABLE = False

from ..config.config import Config
from ..capture.screenshot_capture import ScreenshotCaptureManager
from ..monitoring.roi_monitor import ROIMonitor
from ...utils.keyboard_handler import KeyboardHandler


class UnifiedScreenshotManager:
    """
    Unified screenshot manager that consolidates all screenshot functionality
    Replaces the multiple scattered implementations with a single, clean interface
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.capture_manager = ScreenshotCaptureManager(config)
        self.roi_monitor = ROIMonitor(config)
        self.keyboard_handler = KeyboardHandler(config)
        
        self._monitoring = False
        self._max_screenshots = config.get('max_screenshots', 100)
        self._initialized = False
        
        # Initialize memory storage
        self._screenshots: List[Dict[str, Any]] = []
        self._llm_responses: Dict[int, str] = {}
        
        # Clean up any existing temporary files
        self._cleanup_temp_files()
    
    def initialize(self) -> bool:
        """Initialize all components"""
        # Initialize capture manager
        if not self.capture_manager.initialize():
            print("❌ Failed to initialize screenshot capture")
            return False
        
        # Initialize ROI monitor
        if not self.roi_monitor.initialize():
            print("❌ Failed to initialize ROI monitor")
            return False
        
        # Initialize keyboard handler (optional)
        keyboard_init = self.keyboard_handler.initialize()
        if not keyboard_init:
            print("⚠️  Keyboard handler initialization failed (optional component)")
        
        self._initialized = True
        print("✅ Unified screenshot manager initialized successfully")
        return True
    
    def is_initialized(self) -> bool:
        """Check if the manager is initialized"""
        return self._initialized
    
    # ====================
    # Screenshot Operations
    # ====================
    
    def take_screenshot(self, roi: Optional[Tuple[int, int, int, int]] = None, save_to_temp: bool = True) -> Optional[bytes]:
        """
        Take a screenshot (unified method)
        
        Args:
            roi: Region of interest (left, top, right, bottom). If None, takes full screenshot
            save_to_temp: Whether to save to temporary file
            
        Returns:
            Screenshot data as bytes, or None if failed
        """
        if not self._initialized:
            print("❌ Screenshot manager not initialized")
            return None
        
        if roi is None:
            # Full screen capture
            result = self.capture_manager.capture_full_screen()
        else:
            # ROI capture
            result = self.capture_manager.capture_roi(roi)
        
        if not result.success:
            print(f"❌ Screenshot capture failed: {result.error}")
            return None
        
        screenshot_data = result.data
        
        # Save to temp file if requested
        if save_to_temp and screenshot_data:
            try:
                os.makedirs(os.path.dirname(self.config.temp_screenshot_path), exist_ok=True)
                with open(self.config.temp_screenshot_path, 'wb') as f:
                    f.write(screenshot_data)
            except Exception as e:
                print(f"⚠️  Failed to save screenshot to temp: {e}")
        
        return screenshot_data
    
    def take_full_screenshot(self, save_to_temp: bool = True) -> Optional[bytes]:
        """Take a full screen screenshot"""
        return self.take_screenshot(roi=None, save_to_temp=save_to_temp)
    
    def take_roi_screenshot(self, roi: Optional[Tuple[int, int, int, int]] = None) -> Optional[bytes]:
        """Take a screenshot of a specific region"""
        if roi is None:
            roi = self.config.roi
        return self.take_screenshot(roi=roi, save_to_temp=False)
    
    def take_unified_roi_screenshot(self, roi: Optional[Tuple[int, int, int, int]] = None) -> Optional[bytes]:
        """
        Take a unified ROI screenshot by capturing full screen and cropping
        Ensures consistency between preview and trigger endpoints
        """
        if roi is None:
            roi = self.config.roi
        
        if not roi:
            print("❌ No ROI configured for unified screenshot")
            return None
        
        # Validate ROI format
        if len(roi) != 4:
            print(f"❌ Invalid ROI format: {roi}. Expected (left, top, right, bottom)")
            return None
        
        left, top, right, bottom = roi
        if left >= right or top >= bottom:
            print(f"❌ Invalid ROI coordinates: {roi}")
            return None
        
        # Capture full screen first
        full_screenshot = self.take_full_screenshot(save_to_temp=False)
        if not full_screenshot:
            print("❌ Failed to capture full screen for ROI cropping")
            return None
        
        # Crop the ROI
        return self._crop_roi_from_screenshot(full_screenshot, roi)
    
    def _crop_roi_from_screenshot(self, screenshot_data: bytes, roi: Tuple[int, int, int, int]) -> Optional[bytes]:
        """Crop ROI from full screenshot data"""
        if not PIL_AVAILABLE:
            print("❌ PIL not available, cannot crop ROI from full screenshot")
            return None
        
        try:
            left, top, right, bottom = roi
            
            # Load the full screenshot
            img = Image.open(io.BytesIO(screenshot_data))
            img_width, img_height = img.size
            
            # Validate and adjust ROI coordinates
            adjusted_left = max(0, min(left, img_width - 1))
            adjusted_top = max(0, min(top, img_height - 1))
            adjusted_right = max(adjusted_left + 1, min(right, img_width))
            adjusted_bottom = max(adjusted_top + 1, min(bottom, img_height))
            
            # Log if coordinates were adjusted
            if (adjusted_left, adjusted_top, adjusted_right, adjusted_bottom) != (left, top, right, bottom):
                print(f"⚠️  ROI coordinates adjusted to fit image bounds:")
                print(f"   Original: ({left}, {top}, {right}, {bottom})")
                print(f"   Adjusted: ({adjusted_left}, {adjusted_top}, {adjusted_right}, {adjusted_bottom})")
            
            # Crop the image
            cropped_img = img.crop((adjusted_left, adjusted_top, adjusted_right, adjusted_bottom))
            
            # Convert back to bytes
            output = io.BytesIO()
            cropped_img.save(output, format='PNG')
            
            return output.getvalue()
            
        except Exception as e:
            print(f"❌ Failed to crop ROI from screenshot: {e}")
            return None
    
    # ====================
    # Monitoring Operations
    # ====================
    
    def start_roi_monitoring(self, roi: Tuple[int, int, int, int]) -> bool:
        """Start monitoring a region of interest"""
        if not self._initialized:
            return False
        
        if self._monitoring:
            self.stop_roi_monitoring()
        
        success = self.roi_monitor.start_monitoring(roi)
        if success:
            self._monitoring = True
            # Start keyboard handler for monitoring controls
            if self.keyboard_handler.is_available():
                self.keyboard_handler.start_monitoring()
        
        return success
    
    def stop_roi_monitoring(self):
        """Stop ROI monitoring"""
        if self._monitoring:
            self.roi_monitor.stop_monitoring()
            if self.keyboard_handler.is_available():
                self.keyboard_handler.stop_monitoring()
            self._monitoring = False
    
    def is_monitoring(self) -> bool:
        """Check if ROI monitoring is active"""
        return self._monitoring
    
    def get_roi_history(self) -> list:
        """Get the ROI monitoring history"""
        return self.roi_monitor.get_history()
    
    # ====================
    # Screenshot Collection Management
    # ====================
    
    def add_screenshot(self, timestamp: str, screenshot_data: bytes, metadata: Dict[str, Any] = None):
        """Add a screenshot to the collection"""
        screenshot_info = {
            'timestamp': timestamp,
            'data': screenshot_data,
            'size': len(screenshot_data),
            'metadata': metadata or {}
        }
        
        self._screenshots.append(screenshot_info)
        
        # Clean up old screenshots if we exceed the limit
        if len(self._screenshots) > self._max_screenshots:
            self._cleanup_old_screenshots()
    
    def get_screenshot(self, index: int) -> Optional[Dict[str, Any]]:
        """Get a screenshot by index"""
        if 0 <= index < len(self._screenshots):
            return self._screenshots[index]
        return None
    
    def get_screenshot_data(self, index: int) -> Optional[bytes]:
        """Get screenshot data by index"""
        screenshot = self.get_screenshot(index)
        return screenshot['data'] if screenshot else None
    
    def get_all_screenshots(self) -> List[Dict[str, Any]]:
        """Get all screenshots with metadata"""
        return [
            {
                'timestamp': s['timestamp'],
                'size': s['size'],
                'metadata': s['metadata'],
                'llm_response': self._llm_responses.get(i)
            }
            for i, s in enumerate(self._screenshots)
        ]
    
    def get_screenshot_count(self) -> int:
        """Get the number of screenshots"""
        return len(self._screenshots)
    
    def get_latest_screenshot(self) -> Optional[Dict[str, Any]]:
        """Get the most recent screenshot"""
        return self._screenshots[-1] if self._screenshots else None
    
    def clear_all_screenshots(self) -> bool:
        """Clear all screenshots from memory"""
        try:
            screenshot_count = len(self._screenshots)
            self._screenshots.clear()
            self._llm_responses.clear()
            print(f"✅ Cleared {screenshot_count} screenshots from memory")
            return True
        except Exception as e:
            print(f"❌ Failed to clear screenshots: {e}")
            return False
    
    def delete_screenshot(self, index: int) -> bool:
        """Delete a screenshot by index"""
        if 0 <= index < len(self._screenshots):
            del self._screenshots[index]
            
            # Adjust LLM response indices
            new_responses = {}
            for idx, response in self._llm_responses.items():
                if idx < index:
                    new_responses[idx] = response
                elif idx > index:
                    new_responses[idx - 1] = response
            self._llm_responses = new_responses
            
            return True
        return False
    
    # ====================
    # Analysis and LLM Integration
    # ====================
    
    def set_llm_response(self, index: int, response: str):
        """Set LLM response for a screenshot"""
        if 0 <= index < len(self._screenshots):
            self._llm_responses[index] = response
    
    def get_llm_response(self, index: int) -> Optional[str]:
        """Get LLM response for a screenshot"""
        return self._llm_responses.get(index)
    
    # ====================
    # Utility Methods
    # ====================
    
    def screenshot_to_base64(self, screenshot_bytes: bytes) -> str:
        """Convert screenshot bytes to base64 string"""
        return base64.b64encode(screenshot_bytes).decode('utf-8')
    
    def base64_to_screenshot(self, base64_str: str) -> bytes:
        """Convert base64 string to screenshot bytes"""
        return base64.b64decode(base64_str)
    
    def resize_screenshot(self, screenshot_bytes: bytes, max_width: int = 1920, max_height: int = 1080) -> bytes:
        """Resize screenshot if it's too large"""
        if not PIL_AVAILABLE:
            return screenshot_bytes
        
        try:
            img = Image.open(io.BytesIO(screenshot_bytes))
            
            # Check if resize is needed
            if img.width <= max_width and img.height <= max_height:
                return screenshot_bytes
            
            # Calculate new dimensions while maintaining aspect ratio
            ratio = min(max_width / img.width, max_height / img.height)
            new_width = int(img.width * ratio)
            new_height = int(img.height * ratio)
            
            # Resize image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert back to bytes
            output = io.BytesIO()
            resized_img.save(output, format='PNG')
            return output.getvalue()
            
        except Exception as e:
            print(f"❌ Failed to resize screenshot: {e}")
            return screenshot_bytes
    
    def compare_screenshots(self, screenshot1: bytes, screenshot2: bytes) -> float:
        """Compare two screenshots and return difference score"""
        if not PIL_AVAILABLE or not NUMPY_AVAILABLE:
            return 0.0
        
        try:
            img1 = Image.open(io.BytesIO(screenshot1))
            img2 = Image.open(io.BytesIO(screenshot2))
            
            # Ensure images are the same size
            if img1.size != img2.size:
                return float('inf')
            
            # Convert to numpy arrays
            arr1 = np.array(img1)
            arr2 = np.array(img2)
            
            # Calculate mean absolute difference
            diff = np.mean(np.abs(arr1.astype(float) - arr2.astype(float)))
            return float(diff)
            
        except Exception as e:
            print(f"❌ Error comparing screenshots: {e}")
            return 0.0
    
    def has_significant_change(self, new_screenshot: bytes, threshold: float = None) -> bool:
        """Check if new screenshot has significant changes from the last one"""
        if not self._screenshots:
            return False
        
        if threshold is None:
            threshold = self.config.change_threshold
        
        last_screenshot = self._screenshots[-1]['data']
        diff = self.compare_screenshots(last_screenshot, new_screenshot)
        
        return diff > threshold
    
    # ====================
    # Status and Configuration
    # ====================
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information"""
        latest = self.get_latest_screenshot()
        capabilities = self.capture_manager.get_capabilities() if self._initialized else {}
        
        return {
            'initialized': self._initialized,
            'screenshot_count': len(self._screenshots),
            'last_capture': latest['timestamp'] if latest else 'Never',
            'monitoring': self._monitoring,
            'roi': self.config.roi,
            'capture_method': capabilities.get('primary', {}).get('method', 'Unknown'),
            'fallback_methods': len(capabilities.get('fallbacks', [])),
            'memory_usage': self.get_memory_usage(),
            'settings': {
                'change_threshold': self.config.change_threshold,
                'check_interval': self.config.check_interval,
                'max_screenshots': self._max_screenshots,
                'llm_enabled': self.config.llm_enabled
            }
        }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information"""
        total_size = sum(s['size'] for s in self._screenshots)
        return {
            'screenshot_count': len(self._screenshots),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'max_screenshots': self._max_screenshots,
            'llm_responses_count': len(self._llm_responses),
            'usage_percentage': round((len(self._screenshots) / self._max_screenshots) * 100, 1) if self._max_screenshots > 0 else 0
        }
    
    # ====================
    # Resource Management
    # ====================
    
    def _cleanup_old_screenshots(self):
        """Remove old screenshots to stay within limits"""
        if self.config.get('auto_cleanup', True):
            excess = len(self._screenshots) - self._max_screenshots
            if excess > 0:
                # Remove oldest screenshots
                for _ in range(excess):
                    self._screenshots.pop(0)
                
                # Adjust LLM response indices
                new_responses = {}
                for idx, response in self._llm_responses.items():
                    new_idx = idx - excess
                    if new_idx >= 0:
                        new_responses[new_idx] = response
                self._llm_responses = new_responses
    
    def _cleanup_temp_files(self):
        """Clean up any existing temporary files"""
        try:
            if hasattr(self.config, 'temp_screenshot_path') and os.path.exists(self.config.temp_screenshot_path):
                os.remove(self.config.temp_screenshot_path)
        except Exception as e:
            print(f"⚠️  Failed to clean up temp files: {e}")
    
    def cleanup(self):
        """Clean up all resources and memory"""
        # Stop monitoring first
        self.stop_roi_monitoring()
        
        # Clear memory storage
        screenshot_count = len(self._screenshots)
        self._screenshots.clear()
        self._llm_responses.clear()
        
        # Clean up capture manager
        if hasattr(self.capture_manager, 'cleanup'):
            self.capture_manager.cleanup()
        
        # Clean up temporary files
        self._cleanup_temp_files()
        
        self._initialized = False
        
        if screenshot_count > 0:
            print(f"✅ Cleanup complete: cleared {screenshot_count} screenshots")
        else:
            print("✅ Cleanup complete")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except:
            pass


# Backward compatibility aliases - these point to the unified manager
ScreenshotManager = UnifiedScreenshotManager
ScreenshotManagerRefactored = UnifiedScreenshotManager

# Export the unified interface
__all__ = [
    'UnifiedScreenshotManager',
    'ScreenshotManager',  # Backward compatibility
    'ScreenshotManagerRefactored'  # Backward compatibility
]
