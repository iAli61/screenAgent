"""
ROI monitoring for detecting changes in the region of interest
"""
import time
import threading
from typing import Optional, Callable, Dict, Any
from datetime import datetime

from ..config.config import Config
from ..capture.screenshot_capture import ScreenshotCapture


class ROIMonitor:
    """Monitors the region of interest for changes and triggers screenshots"""
    
    def __init__(self, config: Config):
        self.config = config
        self.screenshot_capture = ScreenshotCapture(config)
        self._running = False
        self._thread = None
        self._last_screenshot = None
        self._monitor_start_time = None
        self._change_callbacks = []
        self._history = []
    
    def initialize(self) -> bool:
        """Initialize the ROI monitor"""
        return self.screenshot_capture.initialize()
    
    def start(self):
        """Start monitoring the ROI"""
        if self._running:
            return
        
        self._running = True
        self._monitor_start_time = datetime.now()
        print(f"🔍 Starting ROI monitoring (checking every {self.config.check_interval}s)")
        
        while self._running:
            try:
                self._check_for_changes()
                time.sleep(self.config.check_interval)
            except Exception as e:
                print(f"Error in ROI monitoring: {e}")
                time.sleep(1)  # Brief pause before continuing
    
    def stop(self):
        """Stop monitoring the ROI"""
        if self._running:
            self._running = False
            print("🛑 ROI monitoring stopped")
    
    def is_running(self) -> bool:
        """Check if monitoring is active"""
        return self._running
    
    def add_change_callback(self, callback: Callable[[bytes], None]):
        """Add a callback to be called when changes are detected"""
        self._change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[bytes], None]):
        """Remove a change callback"""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)
    
    def force_screenshot(self) -> Optional[bytes]:
        """Force a screenshot regardless of changes"""
        try:
            roi = self.config.roi
            screenshot = self.screenshot_capture.capture_roi(roi)
            
            if screenshot:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._history.append({
                    'timestamp': timestamp,
                    'size': len(screenshot),
                    'roi': roi
                })
                self._last_screenshot = screenshot
                
                # Notify callbacks
                for callback in self._change_callbacks:
                    try:
                        callback(screenshot)
                    except Exception as e:
                        print(f"Error in change callback: {e}")
                
                print(f"📸 Manual screenshot taken at {timestamp}")
                return screenshot
        except Exception as e:
            print(f"Error taking manual screenshot: {e}")
        
        return None
    
    def get_monitoring_duration(self) -> float:
        """Get how long monitoring has been running (in seconds)"""
        if self._monitor_start_time:
            return (datetime.now() - self._monitor_start_time).total_seconds()
        return 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring status"""
        duration = self.get_monitoring_duration()
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        
        return {
            'active': self._running,
            'duration_seconds': duration,
            'duration_formatted': f"{hours}h {minutes}m",
            'roi': self.config.roi,
            'check_interval': self.config.check_interval,
            'change_threshold': self.config.change_threshold,
            'screenshot_count': len(self._history)
        }
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update monitoring settings"""
        try:
            if 'change_threshold' in settings:
                self.config.change_threshold = float(settings['change_threshold'])
            
            if 'check_interval' in settings:
                self.config.check_interval = float(settings['check_interval'])
            
            if 'roi' in settings:
                roi = settings['roi']
                if isinstance(roi, (list, tuple)) and len(roi) == 4:
                    self.config.roi = tuple(map(int, roi))
            
            print("⚙️ Monitoring settings updated")
            return True
            
        except Exception as e:
            print(f"Error updating monitoring settings: {e}")
            return False
    
    def _check_for_changes(self):
        """Check for changes in the ROI and take screenshot if needed"""
        try:
            # Ensure screenshot capture is initialized
            if not self.screenshot_capture._initialized:
                if not self.screenshot_capture.initialize():
                    print("❌ Failed to initialize screenshot capture in ROI monitor")
                    return
            
            roi = self.config.roi
            current_screenshot = self.screenshot_capture.capture_roi(roi)
            
            if not current_screenshot:
                return
            
            # Check if this is the first screenshot or if there are significant changes
            should_save = False
            
            if self._last_screenshot is None:
                # First screenshot
                should_save = True
                print("📸 First ROI screenshot captured")
            else:
                # Check for changes by comparing file sizes (simple method)
                if len(current_screenshot) != len(self._last_screenshot):
                    should_save = True
                    print("📸 Changes detected, capturing screenshot")
            
            if should_save:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._history.append({
                    'timestamp': timestamp,
                    'size': len(current_screenshot),
                    'roi': roi
                })
                self._last_screenshot = current_screenshot
                
                # Notify callbacks
                for callback in self._change_callbacks:
                    try:
                        callback(current_screenshot)
                    except Exception as e:
                        print(f"Error in change callback: {e}")
            
        except Exception as e:
            print(f"Error checking for changes: {e}")
    
    def reset_baseline(self):
        """Reset the baseline screenshot for change detection"""
        self._last_screenshot = None
        print("🔄 ROI monitoring baseline reset")
    
    def start_monitoring(self, roi: tuple) -> bool:
        """Start monitoring a specific ROI"""
        # Ensure screenshot capture is initialized before starting monitoring
        if not self.screenshot_capture._initialized:
            if not self.screenshot_capture.initialize():
                print("❌ Cannot start ROI monitoring: screenshot capture failed to initialize")
                return False
        
        self.config.roi = roi
        self.start()
        return True
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.stop()
    
    def get_history(self) -> list:
        """Get monitoring history"""
        return self._history
