"""
Refactored Screenshot Manager
Part of Phase 1.4 - Screenshot Manager Module Refactoring

This is the new modular screenshot manager that coordinates all screenshot operations
using the orchestrator pattern and event-driven architecture.
"""
from typing import Optional, Dict, Any, List
from ..config import Config
from .screenshot_orchestrator import ScreenshotOrchestrator, ScreenshotManager as LegacyManager


class ScreenshotManagerRefactored:
    """
    New modular screenshot manager
    Uses the orchestrator for all operations
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.orchestrator = ScreenshotOrchestrator(config)
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize the screenshot manager"""
        success = self.orchestrator.initialize()
        self._initialized = success
        return success
    
    def is_initialized(self) -> bool:
        """Check if the manager is initialized"""
        return self._initialized
    
    # Screenshot Operations
    def take_screenshot(self, roi: Optional[tuple] = None, save_to_temp: bool = False) -> Optional[str]:
        """
        Take a screenshot
        Args:
            roi: Region of interest (x, y, width, height). If None, uses configured ROI
            save_to_temp: Whether to save to temp file
        Returns:
            Screenshot ID if successful, None otherwise
        """
        if not self._initialized:
            return None
        
        if roi is None:
            # Full screen
            return self.orchestrator.take_full_screenshot(save_to_temp)
        else:
            # ROI screenshot
            return self.orchestrator.take_manual_screenshot(roi)
    
    def take_full_screenshot(self, save_to_temp: bool = True) -> Optional[str]:
        """Take a full screen screenshot"""
        if not self._initialized:
            return None
        return self.orchestrator.take_full_screenshot(save_to_temp)
    
    def take_roi_screenshot(self, roi: Optional[tuple] = None) -> Optional[str]:
        """Take a screenshot of a specific region"""
        if not self._initialized:
            return None
        return self.orchestrator.take_manual_screenshot(roi)
    
    # Monitoring Operations
    def start_monitoring(self, roi: tuple) -> bool:
        """Start monitoring a region of interest"""
        if not self._initialized:
            return False
        return self.orchestrator.start_monitoring(roi)
    
    def stop_monitoring(self) -> None:
        """Stop monitoring"""
        if self._initialized:
            self.orchestrator.stop_monitoring()
    
    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        if not self._initialized:
            return False
        return self.orchestrator.is_monitoring()
    
    # Data Operations
    def get_screenshots(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get screenshots metadata"""
        if not self._initialized:
            return []
        return self.orchestrator.get_screenshots(limit)
    
    def get_screenshot_data(self, screenshot_id: str) -> Optional[bytes]:
        """Get raw screenshot data"""
        if not self._initialized:
            return None
        return self.orchestrator.get_screenshot_data(screenshot_id)
    
    def get_screenshot_base64(self, screenshot_id: str) -> Optional[str]:
        """Get screenshot as base64 string"""
        if not self._initialized:
            return None
        return self.orchestrator.get_screenshot_base64(screenshot_id)
    
    def delete_screenshot(self, screenshot_id: str) -> bool:
        """Delete a specific screenshot"""
        if not self._initialized:
            return False
        return self.orchestrator.delete_screenshot(screenshot_id)
    
    def clear_all_screenshots(self) -> bool:
        """Clear all screenshots"""
        if not self._initialized:
            return False
        return self.orchestrator.clear_all_screenshots()
    
    # Analysis Operations
    def set_analysis_response(self, screenshot_id: str, response: str) -> None:
        """Set analysis response for a screenshot"""
        if self._initialized:
            self.orchestrator.set_analysis_response(screenshot_id, response)
    
    def get_analysis_response(self, screenshot_id: str) -> Optional[str]:
        """Get analysis response for a screenshot"""
        if not self._initialized:
            return None
        return self.orchestrator.get_analysis_response(screenshot_id)
    
    # Utility Operations
    def resize_screenshot(self, screenshot_data: bytes, max_width: int = 1920, max_height: int = 1080) -> bytes:
        """Resize screenshot data"""
        if not self._initialized:
            return screenshot_data
        return self.orchestrator.resize_screenshot(screenshot_data, max_width, max_height)
    
    # Status and Configuration
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status"""
        if not self._initialized:
            return {'error': 'Not initialized'}
        return self.orchestrator.get_status()
    
    def get_screenshot_count(self) -> int:
        """Get number of stored screenshots"""
        if not self._initialized:
            return 0
        
        status = self.orchestrator.get_status()
        return status.get('storage', {}).get('count', 0)
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update settings for all components"""
        if not self._initialized:
            return False
        return self.orchestrator.update_settings(settings)
    
    # Resource Management
    def cleanup(self) -> None:
        """Clean up all resources"""
        if self._initialized:
            self.orchestrator.cleanup()
            self._initialized = False
    
    # Convenience methods for compatibility
    def get_all_screenshots(self) -> List[Dict[str, Any]]:
        """Alias for get_screenshots() for backward compatibility"""
        return self.get_screenshots()
    
    def get_latest_screenshot(self) -> Optional[Dict[str, Any]]:
        """Get the most recent screenshot"""
        screenshots = self.get_screenshots(limit=1)
        return screenshots[0] if screenshots else None
    
    def has_screenshots(self) -> bool:
        """Check if any screenshots are stored"""
        return self.get_screenshot_count() > 0


# Export both the new and legacy managers
# Applications can choose which one to use
__all__ = [
    'ScreenshotManagerRefactored',
    'ScreenshotOrchestrator',
    'LegacyManager'  # For backward compatibility
]
