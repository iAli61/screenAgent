"""
Monitoring Domain Exceptions
"""
from .base_exception import BaseScreenAgentException


class MonitoringException(BaseScreenAgentException):
    """Base exception for monitoring-related errors"""
    pass


class MonitoringSessionNotFoundError(MonitoringException):
    """Exception for monitoring session not found"""
    
    def __init__(self, session_id: str, **kwargs):
        message = f"Monitoring session not found: {session_id}"
        super().__init__(message, error_code="SESSION_NOT_FOUND", status_code=404, **kwargs)
        self.session_id = session_id


class MonitoringSessionConflictError(MonitoringException):
    """Exception for monitoring session conflicts"""
    
    def __init__(self, session_id: str, current_status: str, **kwargs):
        message = f"Cannot perform operation on session {session_id} with status {current_status}"
        super().__init__(message, error_code="SESSION_CONFLICT", status_code=409, **kwargs)
        self.session_id = session_id
        self.current_status = current_status


class MonitoringConfigurationError(MonitoringException):
    """Exception for monitoring configuration errors"""
    
    def __init__(self, message: str = "Invalid monitoring configuration", **kwargs):
        super().__init__(message, error_code="INVALID_CONFIG", status_code=400, **kwargs)


class MonitoringCapacityError(MonitoringException):
    """Exception for monitoring capacity limits"""
    
    def __init__(self, message: str = "Monitoring capacity limit reached", **kwargs):
        super().__init__(message, error_code="CAPACITY_LIMIT", status_code=429, **kwargs)


class MonitoringResourceError(MonitoringException):
    """Exception for monitoring resource errors"""
    
    def __init__(self, message: str = "Monitoring resource error", **kwargs):
        super().__init__(message, error_code="RESOURCE_ERROR", status_code=500, **kwargs)
