"""
Screenshot capture module

This module provides modular screenshot capture functionality with
multiple backend implementations and automatic fallback strategies.
"""

from .capture_interfaces import (
    AbstractScreenshotCapture,
    CaptureResult,
    CaptureMethod,
    ScreenshotCaptureFactory
)

from .capture_implementations import (
    WSLPowerShellCapture,
    WindowsNativeCapture,
    MSSCapture,
    PyAutoGUICapture,
    HeadlessCapture
)

from .screenshot_capture_refactored import ScreenshotCaptureManager

__all__ = [
    'AbstractScreenshotCapture',
    'CaptureResult', 
    'CaptureMethod',
    'ScreenshotCaptureFactory',
    'WSLPowerShellCapture',
    'WindowsNativeCapture',
    'MSSCapture',
    'PyAutoGUICapture',
    'HeadlessCapture',
    'ScreenshotCaptureManager'
]
