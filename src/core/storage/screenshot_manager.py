"""
Screenshot management for ScreenAgent
Coordinates screenshot capture, ROI monitoring, and keyboard handling
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
from ..capture.screenshot_capture import ScreenshotCapture
from ..monitoring.roi_monitor import ROIMonitor
from ...utils.keyboard_handler import KeyboardHandler


class ScreenshotManager:
    """Central manager for screenshot-related functionality"""
    
    def __init__(self, config: Config):
        self.config = config
        self.screenshot_capture = ScreenshotCapture(config)
        self.roi_monitor = ROIMonitor(config)
        self.keyboard_handler = KeyboardHandler(config)
        self._monitoring = False
        self._screenshots: List[Dict[str, Any]] = []
        self._max_screenshots = config.get('max_screenshots', 100)
        self._llm_responses: Dict[int, str] = {}
    
    def initialize(self) -> bool:
        """Initialize all components"""
        if not self.screenshot_capture.initialize():
            print("❌ Failed to initialize screenshot capture")
            return False
        
        if not self.roi_monitor.initialize():
            print("❌ Failed to initialize ROI monitor")
            return False
        
        if not self.keyboard_handler.initialize():
            print("❌ Failed to initialize keyboard handler")
            return False
        
        print("✅ Screenshot manager initialized successfully")
        return True
    
    def take_screenshot(self, save_to_temp: bool = True) -> Optional[bytes]:
        """Take a full screenshot"""
        screenshot = self.screenshot_capture.capture_full_screen()
        
        if screenshot and save_to_temp:
            try:
                os.makedirs(os.path.dirname(self.config.temp_screenshot_path), exist_ok=True)
                with open(self.config.temp_screenshot_path, 'wb') as f:
                    f.write(screenshot)
            except Exception as e:
                print(f"❌ Failed to save screenshot to temp: {e}")
        
        return screenshot
    
    def take_roi_screenshot(self, roi: Tuple[int, int, int, int] = None) -> Optional[bytes]:
        """Take a screenshot of a specific region"""
        if roi is None:
            roi = self.config.roi
        return self.screenshot_capture.capture_roi(roi)
    
    def take_unified_roi_screenshot(self, roi: Tuple[int, int, int, int] = None) -> Optional[bytes]:
        """
        Take a unified ROI screenshot by capturing full screen (same as preview) and cropping ROI.
        This ensures consistency between preview and trigger endpoints for multi-monitor setups.
        
        Args:
            roi: Region of interest as (left, top, right, bottom). If None, uses config.roi
            
        Returns:
            Screenshot data as bytes if successful, None otherwise
            
        Note:
            This method captures a full screenshot first (using the same method as /api/preview)
            and then crops the specified ROI. This ensures that both preview and trigger use
            the same coordinate system and handle multi-monitor setups consistently.
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
            print(f"❌ Invalid ROI coordinates: {roi}. left must be < right and top must be < bottom")
            return None
        
        # Capture full screen using the same method as preview
        full_screenshot = self.screenshot_capture.capture_full_screen()
        if not full_screenshot:
            print("❌ Failed to capture full screen for ROI cropping")
            return None
        
        # Crop the ROI from the full screenshot
        try:
            if not PIL_AVAILABLE:
                print("❌ PIL not available, cannot crop ROI from full screenshot")
                print("   Install PIL with: pip install Pillow")
                return None
            
            # Load the full screenshot
            img = Image.open(io.BytesIO(full_screenshot))
            img_width, img_height = img.size
            
            # Validate and adjust ROI coordinates to stay within image bounds
            adjusted_left = max(0, min(left, img_width - 1))
            adjusted_top = max(0, min(top, img_height - 1))
            adjusted_right = max(adjusted_left + 1, min(right, img_width))
            adjusted_bottom = max(adjusted_top + 1, min(bottom, img_height))
            
            # Log if coordinates were adjusted
            if (adjusted_left, adjusted_top, adjusted_right, adjusted_bottom) != (left, top, right, bottom):
                print(f"⚠️  ROI coordinates adjusted to fit image bounds:")
                print(f"   Original: ({left}, {top}, {right}, {bottom})")
                print(f"   Adjusted: ({adjusted_left}, {adjusted_top}, {adjusted_right}, {adjusted_bottom})")
                print(f"   Image size: {img_width}x{img_height}")
            
            # Crop the image
            cropped_img = img.crop((adjusted_left, adjusted_top, adjusted_right, adjusted_bottom))
            
            # Convert back to bytes
            output = io.BytesIO()
            cropped_img.save(output, format='PNG')
            
            crop_width = adjusted_right - adjusted_left
            crop_height = adjusted_bottom - adjusted_top
            print(f"✅ Unified ROI screenshot: {crop_width}x{crop_height} pixels from full {img_width}x{img_height} image")
            return output.getvalue()
            
        except Exception as e:
            print(f"❌ Failed to crop ROI from full screenshot: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def take_full_screenshot(self, save_to_temp: bool = True) -> bool:
        """Take a full screen screenshot (alias for compatibility)"""
        result = self.take_screenshot(save_to_temp)
        return result is not None
    
    def start_roi_monitoring(self, roi: Tuple[int, int, int, int]) -> bool:
        """Start monitoring a region of interest"""
        if self._monitoring:
            self.stop_roi_monitoring()
        
        success = self.roi_monitor.start_monitoring(roi)
        if success:
            self._monitoring = True
            # Start keyboard handler for monitoring controls
            self.keyboard_handler.start_monitoring()
        
        return success
    
    def stop_roi_monitoring(self):
        """Stop ROI monitoring"""
        if self._monitoring:
            self.roi_monitor.stop_monitoring()
            self.keyboard_handler.stop_monitoring()
            self._monitoring = False
    
    def is_monitoring(self) -> bool:
        """Check if ROI monitoring is active"""
        return self._monitoring
    
    def get_roi_history(self) -> list:
        """Get the ROI monitoring history"""
        return self.roi_monitor.get_history()
    
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
        """Get all screenshots"""
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
    
    def compare_screenshots(self, screenshot1: bytes, screenshot2: bytes) -> float:
        """Compare two screenshots and return difference score"""
        if not PIL_AVAILABLE or not NUMPY_AVAILABLE:
            print("⚠️  PIL/numpy not available, cannot compare screenshots")
            return 0.0
        
        try:
            img1 = Image.open(io.BytesIO(screenshot1))
            img2 = Image.open(io.BytesIO(screenshot2))
            
            # Ensure images are the same size
            if img1.size != img2.size:
                return float('inf')  # Very different if sizes don't match
            
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
            return False  # No previous screenshot to compare
        
        if threshold is None:
            threshold = self.config.change_threshold
        
        last_screenshot = self._screenshots[-1]['data']
        diff = self.compare_screenshots(last_screenshot, new_screenshot)
        
        return diff > threshold
    
    def get_latest_screenshot(self) -> Optional[Dict[str, Any]]:
        """Get the most recent screenshot"""
        return self._screenshots[-1] if self._screenshots else None
    
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
    
    def clear_all_screenshots(self):
        """Clear all screenshots"""
        self._screenshots.clear()
        self._llm_responses.clear()
    
    def set_llm_response(self, index: int, response: str):
        """Set LLM response for a screenshot"""
        if 0 <= index < len(self._screenshots):
            self._llm_responses[index] = response
    
    def get_llm_response(self, index: int) -> Optional[str]:
        """Get LLM response for a screenshot"""
        return self._llm_responses.get(index)
    
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
    
    def get_status(self) -> Dict[str, Any]:
        """Get status information"""
        latest = self.get_latest_screenshot()
        return {
            'screenshot_count': len(self._screenshots),
            'last_capture': latest['timestamp'] if latest else 'Never',
            'monitoring': self._monitoring,
            'roi': self.config.roi,
            'screenshot_method': self.screenshot_capture.method,
            'settings': {
                'change_threshold': self.config.change_threshold,
                'check_interval': self.config.check_interval,
                'llm_enabled': self.config.llm_enabled
            }
        }
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_roi_monitoring()
        
        # Clean up temporary files
        try:
            if os.path.exists(self.config.temp_screenshot_path):
                os.remove(self.config.temp_screenshot_path)
        except Exception as e:
            print(f"⚠️  Failed to clean up temp files: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except:
            pass
    
    def screenshot_to_base64(self, screenshot_bytes: bytes) -> str:
        """Convert screenshot bytes to base64 string"""
        return base64.b64encode(screenshot_bytes).decode('utf-8')
    
    def base64_to_screenshot(self, base64_str: str) -> bytes:
        """Convert base64 string to screenshot bytes"""
        return base64.b64decode(base64_str)
    
    def resize_screenshot(self, screenshot_bytes: bytes, max_width: int = 1920, max_height: int = 1080) -> bytes:
        """Resize screenshot if it's too large"""
        if not PIL_AVAILABLE:
            print("⚠️  PIL not available, cannot resize screenshot")
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
