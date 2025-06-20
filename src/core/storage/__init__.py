"""
Storage and screenshot management module

This module provides storage abstraction, screenshot orchestration,
and comprehensive screenshot management functionality.
"""

from .storage_manager import (
    ScreenshotStorage,
    ScreenshotData,
    ScreenshotMetadata,
    MemoryScreenshotStorage,
    FileSystemScreenshotStorage,
    StorageFactory
)

from .screenshot_orchestrator import ScreenshotOrchestrator

from .screenshot_manager_refactored import ScreenshotManagerRefactored

# Legacy import for backward compatibility  
from .screenshot_manager import ScreenshotManager

__all__ = [
    'ScreenshotStorage',
    'ScreenshotData',
    'ScreenshotMetadata', 
    'MemoryScreenshotStorage',
    'FileSystemScreenshotStorage',
    'StorageFactory',
    'ScreenshotOrchestrator',
    'ScreenshotManagerRefactored',
    'ScreenshotManager'  # Legacy
]
