"""
Storage and screenshot management module

This module provides unified screenshot management functionality.
"""

# Import the unified manager
from .screenshot_manager_unified import UnifiedScreenshotManager, ScreenshotManager

__all__ = [
    'UnifiedScreenshotManager',
    'ScreenshotManager'  # Backward compatibility alias
]
