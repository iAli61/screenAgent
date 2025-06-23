"""
Interfaces layer for the ScreenAgent application
Contains controllers and DTOs for the API layer
"""

from .controllers import (
    ScreenshotController,
    MonitoringController,
    AnalysisController,
    ConfigurationController
)

__all__ = [
    'ScreenshotController',
    'MonitoringController', 
    'AnalysisController',
    'ConfigurationController'
]
