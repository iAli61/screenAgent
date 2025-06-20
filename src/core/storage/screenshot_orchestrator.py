"""
Screenshot orchestrator for coordinating capture, monitoring, and storage
Part of Phase 1.4 - Screenshot Manager Module Refactoring
"""
import io
import base64
import time
import uuid
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from ..config import Config
from ..capture.screenshot_capture_refactored import ScreenshotCaptureManager
from ..monitoring.roi_monitor_refactored import ROIMonitorManager
from .storage_manager import (
    ScreenshotStorage, 
    StorageFactory, 
    ScreenshotData, 
    ScreenshotMetadata
)
from ..events import (
    EventDispatcher,
    emit_event,
    subscribe_to_events,
    ScreenshotCapturedEvent,
    ChangeDetectedEvent,
    EventType
)


class ScreenshotOrchestrator:
    """
    Orchestrates all screenshot-related operations
    Coordinates capture, monitoring, storage, and analysis
    """
    
    def __init__(self, config: Config):
        self.config = config
        
        # Core components
        self.capture_manager = ScreenshotCaptureManager(config)
        self.roi_monitor = ROIMonitorManager(config, self.capture_manager)
        self.storage = StorageFactory.create_default_storage(config)
        
        # State
        self._initialized = False
        self._monitoring_active = False
        
        # Analysis responses (LLM, etc.)
        self._analysis_responses: Dict[str, str] = {}
        
        # Event handling
        self._event_dispatcher = EventDispatcher()
        self._setup_event_handlers()
        
        # Statistics
        self._stats = {
            'total_captures': 0,
            'manual_captures': 0,
            'automatic_captures': 0,
            'failed_captures': 0,
            'changes_detected': 0,
            'session_start': time.time()
        }
    
    def _setup_event_handlers(self):
        """Setup event handlers for coordination"""
        def on_screenshot_captured(event):
            """Handle screenshot captured events"""
            try:
                # Create screenshot metadata
                metadata = ScreenshotMetadata(
                    id=event.event_id,
                    timestamp=event.timestamp,
                    timestamp_formatted=datetime.fromtimestamp(event.timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    size=len(event.screenshot_data),
                    roi=event.roi,
                    capture_method=event.method,
                    tags=['manual' if event.data.get('forced') else 'automatic']
                )
                
                # Store screenshot
                screenshot_data = ScreenshotData(metadata=metadata, data=event.screenshot_data)
                success = self.storage.store_screenshot(screenshot_data)
                
                if success:
                    # Update statistics
                    self._stats['total_captures'] += 1
                    if event.data.get('forced'):
                        self._stats['manual_captures'] += 1
                    else:
                        self._stats['automatic_captures'] += 1
                    
                    print(f"📸 Screenshot stored: {metadata.id[:8]}... ({metadata.size} bytes)")
                else:
                    self._stats['failed_captures'] += 1
                    print(f"❌ Failed to store screenshot: {metadata.id[:8]}...")
                
            except Exception as e:
                self._stats['failed_captures'] += 1
                print(f"❌ Error handling screenshot captured event: {e}")
        
        def on_change_detected(event):
            """Handle change detected events"""
            try:
                # Update change detection statistics in stored metadata
                screenshot_id = event.event_id
                stored_screenshot = self.storage.retrieve_screenshot(screenshot_id)
                
                if stored_screenshot:
                    stored_screenshot.metadata.change_score = event.change_result.change_score
                    stored_screenshot.metadata.confidence = event.change_result.confidence
                    stored_screenshot.metadata.tags.append('change_detected')
                    
                    # Re-store with updated metadata
                    self.storage.store_screenshot(stored_screenshot)
                
                self._stats['changes_detected'] += 1
                
                print(f"🔍 Change detected! Score: {event.change_result.change_score:.3f}, "
                      f"Confidence: {event.change_result.confidence:.2f}")
                
            except Exception as e:
                print(f"❌ Error handling change detected event: {e}")
        
        # Subscribe to events
        subscribe_to_events(EventType.SCREENSHOT_CAPTURED, on_screenshot_captured)
        subscribe_to_events(EventType.CHANGE_DETECTED, on_change_detected)
    
    def initialize(self) -> bool:
        """Initialize all components"""
        try:
            # Initialize capture manager
            if not self.capture_manager.initialize():
                print("❌ Failed to initialize screenshot capture manager")
                return False
            
            # Initialize ROI monitor
            if not self.roi_monitor.initialize():
                print("❌ Failed to initialize ROI monitor")
                return False
            
            self._initialized = True
            print("✅ Screenshot orchestrator initialized successfully")
            
            # Log capabilities
            capture_capabilities = self.capture_manager.get_capabilities()
            print(f"   📋 Capture methods: {len(capture_capabilities['fallbacks']) + 1}")
            print(f"   📋 Detection methods: {len(self.roi_monitor.get_available_detection_methods())}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize screenshot orchestrator: {e}")
            return False
    
    def take_manual_screenshot(self, roi: Optional[tuple] = None) -> Optional[str]:
        """Take a manual screenshot and return the screenshot ID"""
        if not self._initialized:
            print("❌ Orchestrator not initialized")
            return None
        
        try:
            # Use configured ROI if none provided
            if roi is None:
                roi = self.config.roi
                if not roi:
                    print("❌ No ROI configured for screenshot")
                    return None
            
            # Capture screenshot
            result = self.capture_manager.capture_roi(roi)
            
            if not result.success:
                print(f"❌ Manual screenshot failed: {result.error}")
                return None
            
            # Create and emit screenshot captured event
            screenshot_event = ScreenshotCapturedEvent(
                source="ScreenshotOrchestrator",
                screenshot_data=result.data,
                roi=roi,
                method=result.metadata.get('method', 'unknown'),
                capture_time=time.time(),
                forced=True
            )
            
            emit_event(screenshot_event)
            
            return screenshot_event.event_id
            
        except Exception as e:
            print(f"❌ Error taking manual screenshot: {e}")
            return None
    
    def take_full_screenshot(self, save_to_temp: bool = False) -> Optional[str]:
        """Take a full screen screenshot"""
        if not self._initialized:
            print("❌ Orchestrator not initialized")
            return None
        
        try:
            # Capture full screen
            result = self.capture_manager.capture_full_screen()
            
            if not result.success:
                print(f"❌ Full screenshot failed: {result.error}")
                return None
            
            # Save to temp file if requested
            if save_to_temp:
                try:
                    temp_path = self.config.temp_screenshot_path
                    import os
                    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                    with open(temp_path, 'wb') as f:
                        f.write(result.data)
                except Exception as e:
                    print(f"⚠️  Failed to save temp screenshot: {e}")
            
            # Create metadata for full screen capture
            metadata = ScreenshotMetadata(
                id=str(uuid.uuid4()),
                timestamp=time.time(),
                timestamp_formatted=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                size=len(result.data),
                roi=(0, 0, 0, 0),  # Full screen
                capture_method=result.metadata.get('method', 'unknown'),
                tags=['manual', 'full_screen']
            )
            
            # Store screenshot
            screenshot_data = ScreenshotData(metadata=metadata, data=result.data)
            success = self.storage.store_screenshot(screenshot_data)
            
            if success:
                self._stats['total_captures'] += 1
                self._stats['manual_captures'] += 1
                print(f"📸 Full screenshot captured: {metadata.id[:8]}...")
                return metadata.id
            else:
                print("❌ Failed to store full screenshot")
                return None
            
        except Exception as e:
            print(f"❌ Error taking full screenshot: {e}")
            return None
    
    def start_monitoring(self, roi: tuple) -> bool:
        """Start ROI monitoring"""
        if not self._initialized:
            print("❌ Orchestrator not initialized")
            return False
        
        if self._monitoring_active:
            print("⚠️  Monitoring is already active")
            return True
        
        try:
            success = self.roi_monitor.start_monitoring(roi)
            if success:
                self._monitoring_active = True
                print(f"🔍 Monitoring started for ROI: {roi}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error starting monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> None:
        """Stop ROI monitoring"""
        if self._monitoring_active:
            self.roi_monitor.stop_monitoring()
            self._monitoring_active = False
            print("🛑 Monitoring stopped")
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        return self._monitoring_active
    
    def get_screenshots(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get screenshots with metadata (without data)"""
        try:
            screenshots_metadata = self.storage.list_screenshots(limit)
            
            screenshots_list = []
            for metadata in screenshots_metadata:
                screenshot_dict = {
                    'id': metadata.id,
                    'timestamp': metadata.timestamp_formatted,
                    'size': metadata.size,
                    'roi': metadata.roi,
                    'method': metadata.capture_method,
                    'change_score': metadata.change_score,
                    'confidence': metadata.confidence,
                    'tags': metadata.tags,
                    'analysis_response': self._analysis_responses.get(metadata.id)
                }
                screenshots_list.append(screenshot_dict)
            
            return screenshots_list
            
        except Exception as e:
            print(f"❌ Error getting screenshots: {e}")
            return []
    
    def get_screenshot_data(self, screenshot_id: str) -> Optional[bytes]:
        """Get screenshot data by ID"""
        try:
            screenshot = self.storage.retrieve_screenshot(screenshot_id)
            return screenshot.data if screenshot else None
            
        except Exception as e:
            print(f"❌ Error getting screenshot data: {e}")
            return None
    
    def get_screenshot_base64(self, screenshot_id: str) -> Optional[str]:
        """Get screenshot as base64 string"""
        data = self.get_screenshot_data(screenshot_id)
        if data:
            return base64.b64encode(data).decode('utf-8')
        return None
    
    def delete_screenshot(self, screenshot_id: str) -> bool:
        """Delete a screenshot"""
        try:
            success = self.storage.delete_screenshot(screenshot_id)
            if success:
                # Also remove analysis response
                if screenshot_id in self._analysis_responses:
                    del self._analysis_responses[screenshot_id]
                print(f"🗑️  Screenshot deleted: {screenshot_id[:8]}...")
            
            return success
            
        except Exception as e:
            print(f"❌ Error deleting screenshot: {e}")
            return False
    
    def clear_all_screenshots(self) -> bool:
        """Clear all screenshots"""
        try:
            success = self.storage.clear_all()
            if success:
                self._analysis_responses.clear()
                # Reset statistics
                self._stats.update({
                    'total_captures': 0,
                    'manual_captures': 0,
                    'automatic_captures': 0,
                    'failed_captures': 0,
                    'changes_detected': 0
                })
                print("🗑️  All screenshots cleared")
            
            return success
            
        except Exception as e:
            print(f"❌ Error clearing screenshots: {e}")
            return False
    
    def set_analysis_response(self, screenshot_id: str, response: str) -> None:
        """Set analysis response for a screenshot"""
        self._analysis_responses[screenshot_id] = response
        
        # Also update storage metadata if possible
        try:
            screenshot = self.storage.retrieve_screenshot(screenshot_id)
            if screenshot:
                screenshot.metadata.analysis_results['llm_response'] = response
                self.storage.store_screenshot(screenshot)
        except Exception as e:
            print(f"⚠️  Failed to update storage metadata: {e}")
    
    def get_analysis_response(self, screenshot_id: str) -> Optional[str]:
        """Get analysis response for a screenshot"""
        return self._analysis_responses.get(screenshot_id)
    
    def resize_screenshot(self, screenshot_data: bytes, max_width: int = 1920, max_height: int = 1080) -> bytes:
        """Resize screenshot if it's too large"""
        if not PIL_AVAILABLE:
            print("⚠️  PIL not available, cannot resize screenshot")
            return screenshot_data
        
        try:
            img = Image.open(io.BytesIO(screenshot_data))
            
            # Check if resize is needed
            if img.width <= max_width and img.height <= max_height:
                return screenshot_data
            
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
            return screenshot_data
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information"""
        try:
            # Get storage stats
            storage_stats = self.storage.get_storage_stats()
            
            # Get monitoring status
            roi_status = self.roi_monitor.get_status() if self._monitoring_active else None
            
            # Calculate session duration
            session_duration = time.time() - self._stats['session_start']
            
            status = {
                'initialized': self._initialized,
                'monitoring_active': self._monitoring_active,
                'roi_status': roi_status,
                'storage': storage_stats,
                'statistics': self._stats.copy(),
                'session_duration_seconds': session_duration,
                'capabilities': {
                    'capture_methods': len(self.capture_manager.get_capabilities()['fallbacks']) + 1,
                    'detection_methods': len(self.roi_monitor.get_available_detection_methods()),
                    'storage_type': type(self.storage).__name__,
                    'pil_available': PIL_AVAILABLE
                }
            }
            
            return status
            
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return {'error': str(e)}
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update settings for all components"""
        try:
            success = True
            
            # Update ROI monitor settings
            if any(key in settings for key in ['check_interval', 'change_sensitivity', 'detection_method', 'roi']):
                roi_success = self.roi_monitor.update_settings(settings)
                success &= roi_success
            
            # Update storage settings
            if 'max_screenshots' in settings:
                # This would require recreating storage - log for now
                print(f"⚠️  Storage setting change requires restart: max_screenshots={settings['max_screenshots']}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error updating settings: {e}")
            return False
    
    def cleanup(self) -> None:
        """Clean up all resources"""
        try:
            self.stop_monitoring()
            self.capture_manager.cleanup()
            self.roi_monitor.cleanup()
            print("✅ Screenshot orchestrator cleaned up")
            
        except Exception as e:
            print(f"⚠️  Error during cleanup: {e}")


# Backward compatibility wrapper
class ScreenshotManager:
    """Backward compatibility wrapper for the old ScreenshotManager interface"""
    
    def __init__(self, config: Config):
        self._orchestrator = ScreenshotOrchestrator(config)
        self.config = config
        
        # Legacy keyboard handler - would need refactoring too
        from ...utils.keyboard_handler import KeyboardHandler
        self.keyboard_handler = KeyboardHandler(config)
    
    def initialize(self) -> bool:
        """Initialize screenshot manager"""
        keyboard_init = self.keyboard_handler.initialize()
        orchestrator_init = self._orchestrator.initialize()
        return orchestrator_init  # Keyboard is optional
    
    def take_screenshot(self, save_to_temp: bool = True) -> Optional[bytes]:
        """Take a full screenshot"""
        screenshot_id = self._orchestrator.take_full_screenshot(save_to_temp)
        if screenshot_id:
            return self._orchestrator.get_screenshot_data(screenshot_id)
        return None
    
    def take_roi_screenshot(self, roi: tuple = None) -> Optional[bytes]:
        """Take a screenshot of a specific region"""
        screenshot_id = self._orchestrator.take_manual_screenshot(roi)
        if screenshot_id:
            return self._orchestrator.get_screenshot_data(screenshot_id)
        return None
    
    def take_full_screenshot(self, save_to_temp: bool = True) -> bool:
        """Take a full screen screenshot (legacy interface)"""
        result = self._orchestrator.take_full_screenshot(save_to_temp)
        return result is not None
    
    def start_roi_monitoring(self, roi: tuple) -> bool:
        """Start monitoring a region of interest"""
        success = self._orchestrator.start_monitoring(roi)
        if success and self.keyboard_handler.is_available():
            self.keyboard_handler.start_monitoring()
        return success
    
    def stop_roi_monitoring(self):
        """Stop ROI monitoring"""
        self._orchestrator.stop_monitoring()
        if self.keyboard_handler.is_available():
            self.keyboard_handler.stop_monitoring()
    
    def is_monitoring(self) -> bool:
        """Check if ROI monitoring is active"""
        return self._orchestrator.is_monitoring()
    
    def get_all_screenshots(self) -> List[Dict[str, Any]]:
        """Get all screenshots (legacy format)"""
        return self._orchestrator.get_screenshots()
    
    def get_screenshot_count(self) -> int:
        """Get the number of screenshots"""
        storage_stats = self._orchestrator.storage.get_storage_stats()
        return storage_stats['count']
    
    def clear_all_screenshots(self) -> bool:
        """Clear all screenshots from memory"""
        return self._orchestrator.clear_all_screenshots()
    
    def get_status(self) -> Dict[str, Any]:
        """Get status information (simplified for legacy)"""
        full_status = self._orchestrator.get_status()
        
        # Convert to legacy format
        return {
            'screenshot_count': full_status['storage']['count'],
            'last_capture': 'Recent' if full_status['storage']['count'] > 0 else 'Never',
            'monitoring': full_status['monitoring_active'],
            'roi': self.config.roi,
            'screenshot_method': 'orchestrated',
            'settings': {
                'change_threshold': self.config.get('change_threshold', 'N/A'),
                'check_interval': self.config.check_interval,
                'llm_enabled': self.config.llm_enabled
            }
        }
    
    def cleanup(self):
        """Clean up resources"""
        self._orchestrator.cleanup()
        if self.keyboard_handler.is_available():
            self.keyboard_handler.stop_monitoring()
