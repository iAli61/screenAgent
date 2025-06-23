"""
Screenshot Domain Exceptions
"""
from .base_exception import BaseScreenAgentException


class ScreenshotException(BaseScreenAgentException):
    """Base exception for screenshot-related errors"""
    pass


class ScreenshotCaptureError(ScreenshotException):
    """Exception for screenshot capture failures"""
    
    def __init__(self, message: str = "Failed to capture screenshot", **kwargs):
        super().__init__(message, error_code="CAPTURE_FAILED", status_code=500, **kwargs)


class ScreenshotNotFoundError(ScreenshotException):
    """Exception for screenshot not found errors"""
    
    def __init__(self, screenshot_id: str, **kwargs):
        message = f"Screenshot not found: {screenshot_id}"
        super().__init__(message, error_code="SCREENSHOT_NOT_FOUND", status_code=404, **kwargs)
        self.screenshot_id = screenshot_id


class ScreenshotStorageError(ScreenshotException):
    """Exception for screenshot storage errors"""
    
    def __init__(self, message: str = "Screenshot storage error", **kwargs):
        super().__init__(message, error_code="STORAGE_ERROR", status_code=500, **kwargs)


class ScreenshotFormatError(ScreenshotException):
    """Exception for screenshot format/validation errors"""
    
    def __init__(self, message: str = "Invalid screenshot format", **kwargs):
        super().__init__(message, error_code="INVALID_FORMAT", status_code=400, **kwargs)


class ScreenshotPermissionError(ScreenshotException):
    """Exception for screenshot permission errors"""
    
    def __init__(self, message: str = "Screenshot access denied", **kwargs):
        super().__init__(message, error_code="ACCESS_DENIED", status_code=403, **kwargs)
