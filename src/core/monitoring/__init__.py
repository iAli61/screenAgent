"""
ROI monitoring module

This module provides region-of-interest monitoring with change detection.
"""

from .change_detection import (
    AbstractChangeDetector,
    SizeBasedChangeDetector,
    HashBasedChangeDetector,
    PixelDiffChangeDetector,
    ChangeDetectionResult,
    ChangeEvent
)

# Main import - only the existing ROI monitor
from .roi_monitor import ROIMonitor

__all__ = [
    'AbstractChangeDetector',
    'SizeBasedChangeDetector', 
    'HashBasedChangeDetector',
    'PixelDiffChangeDetector',
    'ChangeDetectionResult',
    'ChangeEvent',
    'ROIMonitor'
]
