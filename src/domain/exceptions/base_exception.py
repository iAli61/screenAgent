"""
Base Domain Exceptions
Foundation exception classes for the ScreenAgent domain
"""


class BaseScreenAgentException(Exception):
    """Base exception for all ScreenAgent domain errors"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.status_code = status_code
    
    def __str__(self):
        return self.message
    
    def to_dict(self):
        """Convert exception to dictionary for API responses"""
        return {
            'type': self.__class__.__name__,
            'message': self.message,
            'code': self.error_code,
            'details': self.details,
            'status_code': self.status_code
        }


class DomainValidationError(BaseScreenAgentException):
    """Exception for domain validation errors"""
    
    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(message, status_code=400, **kwargs)
        self.field = field


class DomainNotFoundError(BaseScreenAgentException):
    """Exception for not found errors"""
    
    def __init__(self, resource_type: str, resource_id: str = None, **kwargs):
        message = f"{resource_type} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, status_code=404, **kwargs)
        self.resource_type = resource_type
        self.resource_id = resource_id


class DomainConflictError(BaseScreenAgentException):
    """Exception for conflict errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=409, **kwargs)


class DomainPermissionError(BaseScreenAgentException):
    """Exception for permission/authorization errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=403, **kwargs)


class DomainConfigurationError(BaseScreenAgentException):
    """Exception for configuration errors"""
    
    def __init__(self, message: str, **kwargs):
        super().__init__(message, status_code=500, **kwargs)
