"""
Utility modules

This module provides platform detection, keyboard handling,
and other utility functions.
"""

from .platform_detection import (
    is_wsl,
    is_linux_with_display,
    is_windows,
    get_platform_info,
    get_recommended_screenshot_method
)

from .keyboard_handler import KeyboardHandler

__all__ = [
    'is_wsl',
    'is_linux_with_display',
    'is_windows',
    'get_platform_info',
    'get_recommended_screenshot_method',
    'KeyboardHandler'
]
