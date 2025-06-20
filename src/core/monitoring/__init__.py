"""
ROI monitoring module

This module provides region-of-interest monitoring with pluggable
change detection strategies and event-driven architecture.
"""

from .change_detection import (
    AbstractChangeDetector,
    SizeBasedChangeDetector,
    HashBasedChangeDetector,
    PixelDiffChangeDetector,
    ChangeDetectionResult,
    ChangeEvent
)

from .roi_monitor_refactored import ROIMonitorManager

# Legacy import for backward compatibility
from .roi_monitor import ROIMonitor

__all__ = [
    'AbstractChangeDetector',
    'SizeBasedChangeDetector', 
    'HashBasedChangeDetector',
    'PixelDiffChangeDetector',
    'ChangeDetectionResult',
    'ChangeEvent',
    'ROIMonitorManager',
    'ROIMonitor'  # Legacy
]
