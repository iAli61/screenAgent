"""
Logging Middleware
Request/response logging and performance monitoring
"""
import logging
import time
import uuid
from typing import Optional
from flask import Flask, request, g
from werkzeug.local import LocalProxy

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests and responses"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize logging middleware for Flask app"""
        self.app = app
        
        # Setup request logging
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)
        
        # Configure structured logging
        self._setup_logging(app)
    
    def _setup_logging(self, app: Flask):
        """Setup structured logging configuration"""
        log_level = app.config.get('LOG_LEVEL', 'INFO')
        log_format = app.config.get('LOG_FORMAT', 
            '%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s'
        )
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format=log_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Configure specific loggers
        loggers = [
            'screenAgent.api',
            'screenAgent.domain',
            'screenAgent.infrastructure',
            'werkzeug'
        ]
        
        for logger_name in loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(getattr(logging, log_level.upper()))
    
    def before_request(self):
        """Called before each request"""
        # Generate unique request ID
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()
        
        # Add request ID to request object for error handling
        request.request_id = g.request_id
        
        # Log incoming request
        self._log_request()
    
    def after_request(self, response):
        """Called after each request"""
        # Calculate request duration
        duration = time.time() - g.get('start_time', time.time())
        
        # Log response
        self._log_response(response, duration)
        
        # Add request ID to response headers
        response.headers['X-Request-ID'] = g.get('request_id', 'unknown')
        
        return response
    
    def teardown_request(self, exception=None):
        """Called at the end of each request"""
        if exception:
            logger.error(
                f"Request failed with exception: {exception}",
                extra=self._get_log_context()
            )
    
    def _log_request(self):
        """Log incoming request details"""
        # Skip logging for health checks and static files
        if self._should_skip_logging():
            return
        
        logger.info(
            f"{request.method} {request.path}",
            extra={
                **self._get_log_context(),
                'method': request.method,
                'path': request.path,
                'query_string': request.query_string.decode('utf-8'),
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'content_length': request.content_length or 0,
                'content_type': request.content_type or ''
            }
        )
        
        # Log request body for debug level (excluding sensitive data)
        if logger.isEnabledFor(logging.DEBUG) and request.is_json:
            try:
                body = request.get_json()
                # Remove sensitive fields
                sanitized_body = self._sanitize_request_body(body)
                logger.debug(
                    f"Request body: {sanitized_body}",
                    extra=self._get_log_context()
                )
            except Exception as e:
                logger.debug(
                    f"Could not parse request body: {e}",
                    extra=self._get_log_context()
                )
    
    def _log_response(self, response, duration: float):
        """Log response details"""
        # Skip logging for health checks and static files
        if self._should_skip_logging():
            return
        
        log_level = logging.INFO
        if response.status_code >= 400:
            log_level = logging.WARNING
        if response.status_code >= 500:
            log_level = logging.ERROR
        
        logger.log(
            log_level,
            f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s",
            extra={
                **self._get_log_context(),
                'status_code': response.status_code,
                'duration_seconds': round(duration, 3),
                'response_size': len(response.get_data()),
                'content_type': response.content_type or ''
            }
        )
        
        # Log slow requests
        slow_request_threshold = self.app.config.get('SLOW_REQUEST_THRESHOLD', 2.0)
        if duration > slow_request_threshold:
            logger.warning(
                f"Slow request detected: {duration:.3f}s",
                extra=self._get_log_context()
            )
    
    def _should_skip_logging(self) -> bool:
        """Determine if request should be skipped from logging"""
        skip_paths = ['/health', '/favicon.ico', '/static/']
        return any(request.path.startswith(path) for path in skip_paths)
    
    def _get_log_context(self) -> dict:
        """Get context information for logging"""
        return {
            'request_id': g.get('request_id', 'unknown'),
            'endpoint': request.endpoint or 'unknown',
            'method': request.method,
            'path': request.path
        }
    
    def _sanitize_request_body(self, body) -> dict:
        """Remove sensitive information from request body"""
        if not isinstance(body, dict):
            return body
        
        sensitive_fields = ['password', 'token', 'secret', 'key', 'authorization']
        sanitized = body.copy()
        
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = '***REDACTED***'
        
        return sanitized


def setup_request_logging(app: Flask) -> RequestLoggingMiddleware:
    """Setup request logging middleware for Flask application"""
    middleware = RequestLoggingMiddleware(app)
    return middleware


# Create a logger proxy that includes request context
def get_contextual_logger(name: str = None):
    """Get a logger that includes request context"""
    base_logger = logging.getLogger(name or __name__)
    
    def log_with_context(level, msg, *args, **kwargs):
        extra = kwargs.get('extra', {})
        if hasattr(g, 'request_id'):
            extra.update({
                'request_id': g.request_id,
                'endpoint': getattr(request, 'endpoint', 'unknown') if request else 'unknown'
            })
        kwargs['extra'] = extra
        return base_logger.log(level, msg, *args, **kwargs)
    
    # Create a wrapper that preserves the logger interface
    class ContextualLogger:
        def __getattr__(self, name):
            return getattr(base_logger, name)
        
        def debug(self, msg, *args, **kwargs):
            return log_with_context(logging.DEBUG, msg, *args, **kwargs)
        
        def info(self, msg, *args, **kwargs):
            return log_with_context(logging.INFO, msg, *args, **kwargs)
        
        def warning(self, msg, *args, **kwargs):
            return log_with_context(logging.WARNING, msg, *args, **kwargs)
        
        def error(self, msg, *args, **kwargs):
            return log_with_context(logging.ERROR, msg, *args, **kwargs)
        
        def critical(self, msg, *args, **kwargs):
            return log_with_context(logging.CRITICAL, msg, *args, **kwargs)
    
    return ContextualLogger()
