"""
Refactored ROI monitoring with modular change detection and event system
Part of Phase 1.3 - ROI Monitor Module Refactoring
"""
import time
import threading
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import uuid

from ..config import Config
from .change_detection import (
    AbstractChangeDetector, 
    ChangeDetectorFactory, 
    ChangeDetectionMethod,
    ChangeEvent
)
from ..events import (
    EventDispatcher, 
    emit_event,
    ScreenshotCapturedEvent,
    ChangeDetectedEvent,
    MonitoringStatusEvent,
    ErrorEvent
)


class ROIMonitorManager:
    """
    Refactored ROI monitor with modular change detection and event system
    Separates monitoring logic from change detection and screenshot capture
    """
    
    def __init__(self, config: Config, screenshot_capture_manager=None):
        self.config = config
        self.screenshot_capture_manager = screenshot_capture_manager
        
        # Change detection
        self._change_detector: Optional[AbstractChangeDetector] = None
        self._detection_method = ChangeDetectorFactory.get_recommended_method()
        
        # Monitoring state
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._monitor_start_time: Optional[datetime] = None
        self._monitor_id = str(uuid.uuid4())
        
        # Statistics and history
        self._statistics = {
            'screenshots_taken': 0,
            'changes_detected': 0,
            'monitoring_cycles': 0,
            'errors': 0,
            'last_error': None
        }
        self._change_history: List[ChangeEvent] = []
        self._max_history = 100
        
        # Event handling
        self._event_dispatcher = EventDispatcher()
        self._setup_event_handlers()
        
        # Performance monitoring
        self._performance_metrics = {
            'avg_cycle_time': 0.0,
            'avg_detection_time': 0.0,
            'cycle_times': [],
            'max_cycle_times': 50  # Keep last 50 cycle times
        }
    
    def _setup_event_handlers(self) -> None:
        """Setup internal event handlers"""
        # Handle screenshot captured events
        def on_screenshot_captured(event):
            self._statistics['screenshots_taken'] += 1
        
        # Handle change detected events
        def on_change_detected(event):
            self._statistics['changes_detected'] += 1
            
            # Add to change history
            change_event = ChangeEvent(
                timestamp=event.timestamp,
                screenshot_data=event.screenshot_data,
                roi=event.data['roi'],
                change_result=event.change_result,
                screenshot_id=event.event_id
            )
            
            self._change_history.append(change_event)
            if len(self._change_history) > self._max_history:
                self._change_history.pop(0)
        
        # Handle error events
        def on_error(event):
            self._statistics['errors'] += 1
            self._statistics['last_error'] = {
                'time': event.timestamp,
                'error': event.error,
                'context': event.context
            }
        
        from ..events import EventType
        self._event_dispatcher.subscribe(EventType.SCREENSHOT_CAPTURED, on_screenshot_captured)
        self._event_dispatcher.subscribe(EventType.CHANGE_DETECTED, on_change_detected)
        self._event_dispatcher.subscribe(EventType.ERROR_OCCURRED, on_error)
    
    def initialize(self) -> bool:
        """Initialize the ROI monitor"""
        try:
            # Initialize change detector
            sensitivity = self.config.get('change_sensitivity', 0.5)
            self._change_detector = ChangeDetectorFactory.create_detector(
                self._detection_method, 
                self.config, 
                sensitivity
            )
            
            print(f"✅ ROI monitor initialized with {self._detection_method.value} change detection")
            return True
            
        except Exception as e:
            error_event = ErrorEvent(
                source="ROIMonitorManager",
                error=e,
                context="initialization"
            )
            self._event_dispatcher.emit(error_event)
            print(f"❌ Failed to initialize ROI monitor: {e}")
            return False
    
    def start_monitoring(self, roi: tuple) -> bool:
        """Start monitoring a specific ROI"""
        if self._running:
            print("⚠️  ROI monitoring is already running")
            return False
        
        if not self._change_detector:
            print("❌ Change detector not initialized")
            return False
        
        if not self.screenshot_capture_manager:
            print("❌ Screenshot capture manager not available")
            return False
        
        try:
            # Update ROI configuration
            self.config.roi = roi
            
            # Reset change detector baseline
            self._change_detector.reset_baseline()
            
            # Start monitoring thread
            self._running = True
            self._monitor_start_time = datetime.now()
            self._thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._thread.start()
            
            # Emit monitoring started event
            status_event = MonitoringStatusEvent(
                source="ROIMonitorManager",
                status="started",
                roi=roi
            )
            self._event_dispatcher.emit(status_event)
            
            print(f"🔍 ROI monitoring started for region {roi}")
            print(f"   Check interval: {self.config.check_interval}s")
            print(f"   Detection method: {self._detection_method.value}")
            
            return True
            
        except Exception as e:
            self._running = False
            error_event = ErrorEvent(
                source="ROIMonitorManager",
                error=e,
                context="start_monitoring"
            )
            self._event_dispatcher.emit(error_event)
            print(f"❌ Failed to start ROI monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> None:
        """Stop ROI monitoring"""
        if not self._running:
            return
        
        self._running = False
        
        # Wait for thread to finish
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
        # Emit monitoring stopped event
        status_event = MonitoringStatusEvent(
            source="ROIMonitorManager",
            status="stopped"
        )
        self._event_dispatcher.emit(status_event)
        
        print("🛑 ROI monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while self._running:
            cycle_start = time.time()
            
            try:
                self._monitoring_cycle()
                self._statistics['monitoring_cycles'] += 1
                
                # Update performance metrics
                cycle_time = time.time() - cycle_start
                self._performance_metrics['cycle_times'].append(cycle_time)
                if len(self._performance_metrics['cycle_times']) > self._performance_metrics['max_cycle_times']:
                    self._performance_metrics['cycle_times'].pop(0)
                
                self._performance_metrics['avg_cycle_time'] = sum(self._performance_metrics['cycle_times']) / len(self._performance_metrics['cycle_times'])
                
            except Exception as e:
                error_event = ErrorEvent(
                    source="ROIMonitorManager",
                    error=e,
                    context="monitoring_loop"
                )
                self._event_dispatcher.emit(error_event)
                print(f"❌ Error in monitoring loop: {e}")
            
            # Sleep for the configured interval
            time.sleep(self.config.check_interval)
    
    def _monitoring_cycle(self) -> None:
        """Single monitoring cycle"""
        roi = self.config.roi
        if not roi:
            return
        
        # Capture screenshot
        capture_result = self.screenshot_capture_manager.capture_roi(roi)
        
        if not capture_result.success:
            error_event = ErrorEvent(
                source="ROIMonitorManager",
                error=Exception(capture_result.error),
                context="screenshot_capture"
            )
            self._event_dispatcher.emit(error_event)
            return
        
        # Emit screenshot captured event
        screenshot_event = ScreenshotCapturedEvent(
            source="ROIMonitorManager",
            screenshot_data=capture_result.data,
            roi=roi,
            method=capture_result.metadata.get('method', 'unknown'),
            capture_time=time.time()
        )
        self._event_dispatcher.emit(screenshot_event)
        
        # Perform change detection
        detection_start = time.time()
        change_result = self._change_detector.detect_change(capture_result.data, roi)
        detection_time = time.time() - detection_start
        
        # Update performance metrics
        if hasattr(self._performance_metrics, 'detection_times'):
            self._performance_metrics['detection_times'] = []
        else:
            self._performance_metrics['detection_times'] = []
        
        self._performance_metrics['detection_times'].append(detection_time)
        if len(self._performance_metrics['detection_times']) > 50:
            self._performance_metrics['detection_times'].pop(0)
        
        self._performance_metrics['avg_detection_time'] = sum(self._performance_metrics['detection_times']) / len(self._performance_metrics['detection_times'])
        
        # If change detected, emit change event
        if change_result.changed:
            change_event = ChangeDetectedEvent(
                source="ROIMonitorManager",
                change_result=change_result,
                screenshot_data=capture_result.data,
                roi=roi
            )
            self._event_dispatcher.emit(change_event)
            
            print(f"📸 Change detected! Confidence: {change_result.confidence:.2f}, Score: {change_result.change_score:.3f}")
        
        # Update baseline if needed (for methods that need it)
        if not self._change_detector.has_baseline() or change_result.changed:
            self._change_detector.set_baseline(capture_result.data)
    
    def force_screenshot(self) -> Optional[bytes]:
        """Force a screenshot regardless of changes"""
        if not self.screenshot_capture_manager:
            return None
        
        roi = self.config.roi
        if not roi:
            return None
        
        try:
            capture_result = self.screenshot_capture_manager.capture_roi(roi)
            
            if capture_result.success:
                # Emit screenshot captured event
                screenshot_event = ScreenshotCapturedEvent(
                    source="ROIMonitorManager",
                    screenshot_data=capture_result.data,
                    roi=roi,
                    method=capture_result.metadata.get('method', 'unknown'),
                    capture_time=time.time(),
                    forced=True
                )
                self._event_dispatcher.emit(screenshot_event)
                
                print(f"📸 Manual screenshot taken")
                return capture_result.data
            else:
                print(f"❌ Failed to take manual screenshot: {capture_result.error}")
                return None
                
        except Exception as e:
            error_event = ErrorEvent(
                source="ROIMonitorManager",
                error=e,
                context="force_screenshot"
            )
            self._event_dispatcher.emit(error_event)
            print(f"❌ Error taking manual screenshot: {e}")
            return None
    
    def is_running(self) -> bool:
        """Check if monitoring is active"""
        return self._running
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status"""
        duration = self.get_monitoring_duration()
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        
        status = {
            'active': self._running,
            'monitor_id': self._monitor_id,
            'duration_seconds': duration,
            'duration_formatted': f"{hours}h {minutes}m",
            'roi': self.config.roi,
            'check_interval': self.config.check_interval,
            'change_threshold': self.config.get('change_threshold', 'N/A'),
            'detection_method': self._detection_method.value,
            'statistics': self._statistics.copy(),
            'performance': self._performance_metrics.copy(),
            'change_history_size': len(self._change_history)
        }
        
        # Add change detector info
        if self._change_detector:
            status['detector_info'] = {
                'method': self._change_detector.method_name,
                'sensitivity': self._change_detector.sensitivity,
                'supports_roi_analysis': self._change_detector.supports_roi_analysis,
                'has_baseline': self._change_detector.has_baseline()
            }
        
        return status
    
    def get_monitoring_duration(self) -> float:
        """Get how long monitoring has been running (in seconds)"""
        if self._monitor_start_time:
            return (datetime.now() - self._monitor_start_time).total_seconds()
        return 0.0
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update monitoring settings"""
        try:
            updated = False
            
            if 'check_interval' in settings:
                new_interval = float(settings['check_interval'])
                if new_interval > 0:
                    self.config.check_interval = new_interval
                    updated = True
            
            if 'change_sensitivity' in settings:
                new_sensitivity = float(settings['change_sensitivity'])
                if 0.0 <= new_sensitivity <= 1.0 and self._change_detector:
                    self._change_detector.update_sensitivity(new_sensitivity)
                    updated = True
            
            if 'detection_method' in settings:
                try:
                    new_method = ChangeDetectionMethod(settings['detection_method'])
                    if new_method != self._detection_method:
                        self._detection_method = new_method
                        # Reinitialize detector with new method
                        if self._change_detector:
                            sensitivity = self._change_detector.sensitivity
                            self._change_detector = ChangeDetectorFactory.create_detector(
                                new_method, self.config, sensitivity
                            )
                        updated = True
                except ValueError:
                    print(f"⚠️  Invalid detection method: {settings['detection_method']}")
            
            if 'roi' in settings:
                roi = settings['roi']
                if isinstance(roi, (list, tuple)) and len(roi) == 4:
                    self.config.roi = tuple(map(int, roi))
                    updated = True
            
            if updated:
                print("⚙️ ROI monitoring settings updated")
            
            return updated
            
        except Exception as e:
            error_event = ErrorEvent(
                source="ROIMonitorManager",
                error=e,
                context="update_settings"
            )
            self._event_dispatcher.emit(error_event)
            print(f"❌ Error updating settings: {e}")
            return False
    
    def get_change_history(self, limit: Optional[int] = None) -> List[ChangeEvent]:
        """Get change detection history"""
        history = self._change_history.copy()
        if limit:
            history = history[-limit:]
        return history
    
    def reset_baseline(self) -> None:
        """Reset the change detection baseline"""
        if self._change_detector:
            self._change_detector.reset_baseline()
            print("🔄 Change detection baseline reset")
    
    def get_available_detection_methods(self) -> List[ChangeDetectionMethod]:
        """Get list of available change detection methods"""
        return ChangeDetectorFactory.get_available_methods()
    
    def get_event_dispatcher(self) -> EventDispatcher:
        """Get the event dispatcher for this monitor"""
        return self._event_dispatcher
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.stop_monitoring()
        if self._change_detector:
            self._change_detector.reset_baseline()
        self._change_history.clear()


# Backward compatibility wrapper
class ROIMonitor:
    """Backward compatibility wrapper for the old ROIMonitor interface"""
    
    def __init__(self, config: Config):
        self.config = config
        self._manager = ROIMonitorManager(config)
        self._change_callbacks = []
        
        # Setup callback handling for backward compatibility
        def on_change_detected(event):
            for callback in self._change_callbacks:
                try:
                    callback(event.screenshot_data)
                except Exception as e:
                    print(f"Error in change callback: {e}")
        
        from ..events import EventType
        self._manager.get_event_dispatcher().subscribe(EventType.CHANGE_DETECTED, on_change_detected)
    
    def initialize(self) -> bool:
        """Initialize the ROI monitor"""
        return self._manager.initialize()
    
    def start(self):
        """Start monitoring the ROI"""
        roi = self.config.roi
        if roi:
            self._manager.start_monitoring(roi)
        else:
            print("❌ No ROI configured for monitoring")
    
    def stop(self):
        """Stop monitoring the ROI"""
        self._manager.stop_monitoring()
    
    def is_running(self) -> bool:
        """Check if monitoring is active"""
        return self._manager.is_running()
    
    def add_change_callback(self, callback: Callable[[bytes], None]):
        """Add a callback to be called when changes are detected"""
        self._change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[bytes], None]):
        """Remove a change callback"""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)
    
    def force_screenshot(self) -> Optional[bytes]:
        """Force a screenshot regardless of changes"""
        return self._manager.force_screenshot()
    
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring status"""
        return self._manager.get_status()
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update monitoring settings"""
        return self._manager.update_settings(settings)
    
    def start_monitoring(self, roi: tuple) -> bool:
        """Start monitoring a specific ROI"""
        return self._manager.start_monitoring(roi)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        return self._manager.stop_monitoring()
    
    def get_history(self) -> list:
        """Get monitoring history (simplified for backward compatibility)"""
        change_history = self._manager.get_change_history()
        return [
            {
                'timestamp': datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                'size': len(event.screenshot_data),
                'roi': event.roi,
                'confidence': event.change_result.confidence,
                'method': event.change_result.method
            }
            for event in change_history
        ]
