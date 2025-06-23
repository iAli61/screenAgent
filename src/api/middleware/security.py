"""
Security Middleware
Authentication, authorization, rate limiting, and security headers
"""
import time
import hashlib
import hmac
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from collections import defaultdict, deque
from flask import Flask, request, jsonify, g
from werkzeug.exceptions import Unauthorized, Forbidden, TooManyRequests
import logging

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration"""
    def __init__(self):
        self.api_key_header = 'X-API-Key'
        self.rate_limit_header = 'X-RateLimit-Limit'
        self.rate_remaining_header = 'X-RateLimit-Remaining'
        self.rate_reset_header = 'X-RateLimit-Reset'
        self.cors_origins = ['http://localhost:3000', 'http://127.0.0.1:3000']
        self.cors_methods = ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']
        self.cors_headers = ['Content-Type', 'Authorization', 'X-API-Key', 'X-Request-ID']


class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.clients = defaultdict(lambda: deque())
        self.default_limits = {
            'requests_per_minute': 60,
            'requests_per_hour': 1000,
            'requests_per_day': 10000
        }
        self.endpoint_limits = {
            '/api/screenshots/trigger': {'requests_per_minute': 10},
            '/api/monitoring/sessions': {'requests_per_minute': 20},
            '/api/analysis/analyze': {'requests_per_minute': 5}
        }
    
    def is_allowed(self, client_id: str, endpoint: str = None) -> tuple[bool, Dict[str, Any]]:
        """Check if request is allowed and return rate limit info"""
        now = time.time()
        
        # Get limits for endpoint or use defaults
        limits = self.endpoint_limits.get(endpoint, self.default_limits)
        
        # Clean old entries and check limits
        client_requests = self.clients[client_id]
        
        # Check minute limit
        minute_ago = now - 60
        while client_requests and client_requests[0] < minute_ago:
            client_requests.popleft()
        
        minute_limit = limits.get('requests_per_minute', self.default_limits['requests_per_minute'])
        if len(client_requests) >= minute_limit:
            return False, {
                'limit': minute_limit,
                'remaining': 0,
                'reset': int(client_requests[0] + 60)
            }
        
        # Add current request
        client_requests.append(now)
        
        return True, {
            'limit': minute_limit,
            'remaining': minute_limit - len(client_requests),
            'reset': int(now + 60)
        }


class APIKeyAuth:
    """API Key authentication"""
    
    def __init__(self, valid_keys: Optional[List[str]] = None):
        self.valid_keys = set(valid_keys or [])
        # Default development key (should be removed in production)
        self.valid_keys.add('dev-key-12345')
    
    def authenticate(self, api_key: str) -> bool:
        """Authenticate API key"""
        return api_key in self.valid_keys
    
    def add_key(self, api_key: str):
        """Add valid API key"""
        self.valid_keys.add(api_key)
    
    def remove_key(self, api_key: str):
        """Remove API key"""
        self.valid_keys.discard(api_key)


class SecurityMiddleware:
    """Main security middleware class"""
    
    def __init__(self, app: Optional[Flask] = None):
        self.config = SecurityConfig()
        self.rate_limiter = RateLimiter()
        self.api_auth = APIKeyAuth()
        self.app = app
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize security middleware for Flask app"""
        self.app = app
        
        # Register before_request handlers
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Configure CORS
        self._setup_cors(app)
    
    def before_request(self):
        """Run security checks before each request"""
        # Skip security for health checks and CORS preflight
        if self._should_skip_security():
            return
        
        # Check rate limits
        self._check_rate_limits()
        
        # Authenticate request
        self._authenticate_request()
        
        # Validate request headers
        self._validate_headers()
    
    def after_request(self, response):
        """Add security headers to response"""
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add rate limit headers if available
        if hasattr(g, 'rate_limit_info'):
            response.headers[self.config.rate_limit_header] = str(g.rate_limit_info['limit'])
            response.headers[self.config.rate_remaining_header] = str(g.rate_limit_info['remaining'])
            response.headers[self.config.rate_reset_header] = str(g.rate_limit_info['reset'])
        
        return response
    
    def _should_skip_security(self) -> bool:
        """Check if security should be skipped for this request"""
        skip_paths = ['/health', '/favicon.ico', '/api/config/health', '/api/config/status', 
                      "/api/config/docs", '/api/screenshots/screenshots', '/api/monitoring/sessions',
                      '/api/*', '/docs/', '/swaggerui/', '/.well-known/']
        skip_methods = ['OPTIONS']
        skip_prefixes = ['/static/', '/swaggerui/', '/api/doc', '/api/', '/docs']
        
        return (request.path in skip_paths or 
                request.method in skip_methods or
                any(request.path.startswith(prefix) for prefix in skip_prefixes))
    
    def _check_rate_limits(self):
        """Check rate limits for the request"""
        client_id = self._get_client_id()
        endpoint = request.endpoint
        
        allowed, rate_info = self.rate_limiter.is_allowed(client_id, endpoint)
        g.rate_limit_info = rate_info
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for client {client_id}")
            raise TooManyRequests('Rate limit exceeded')
    
    def _authenticate_request(self):
        """Authenticate the request"""
        # Skip authentication for certain endpoints
        if self._should_skip_auth():
            return
        
        api_key = request.headers.get(self.config.api_key_header)
        
        if not api_key:
            logger.warning(f"Missing API key for {request.path}")
            raise Unauthorized('API key required')
        
        if not self.api_auth.authenticate(api_key):
            logger.warning(f"Invalid API key for {request.path}")
            raise Unauthorized('Invalid API key')
        
        g.authenticated = True
        g.api_key = api_key
    
    def _should_skip_auth(self) -> bool:
        """Check if authentication should be skipped"""
        public_endpoints = ['/health', '/api/status']
        return request.path in public_endpoints
    
    def _validate_headers(self):
        """Validate request headers"""
        # Check Content-Type for POST/PUT requests
        if request.method in ['POST', 'PUT'] and request.content_length:
            content_type = request.content_type
            if not content_type or not content_type.startswith('application/json'):
                logger.warning(f"Invalid content type: {content_type}")
                # Don't raise error, let validation middleware handle it
        
        # Check for suspicious headers
        suspicious_headers = ['X-Forwarded-For', 'X-Real-IP']
        for header in suspicious_headers:
            if header in request.headers:
                logger.info(f"Request with {header}: {request.headers[header]}")
    
    def _get_client_id(self) -> str:
        """Get client identifier for rate limiting"""
        # Try to get client ID from various sources
        client_id = (request.headers.get('X-Client-ID') or
                    request.headers.get(self.config.api_key_header) or
                    request.remote_addr or
                    'unknown')
        
        # Hash the client ID for privacy
        return hashlib.sha256(client_id.encode()).hexdigest()[:16]
    
    def _setup_cors(self, app: Flask):
        """Setup CORS configuration"""
        @app.after_request
        def after_request(response):
            origin = request.headers.get('Origin')
            
            # Check if origin is allowed
            if origin in self.config.cors_origins or self.app.config.get('DEBUG', False):
                response.headers['Access-Control-Allow-Origin'] = origin
                response.headers['Access-Control-Allow-Methods'] = ', '.join(self.config.cors_methods)
                response.headers['Access-Control-Allow-Headers'] = ', '.join(self.config.cors_headers)
                response.headers['Access-Control-Allow-Credentials'] = 'true'
                response.headers['Access-Control-Max-Age'] = '3600'
            
            return response


def require_api_key(f: Callable) -> Callable:
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('authenticated', False):
            raise Unauthorized('API key authentication required')
        return f(*args, **kwargs)
    return decorated_function


def require_role(role: str) -> Callable:
    """Decorator to require specific role (placeholder for future implementation)"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Placeholder for role-based authorization
            # In a real implementation, you'd check user roles here
            if not g.get('authenticated', False):
                raise Unauthorized('Authentication required')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def rate_limit(requests_per_minute: int = None, requests_per_hour: int = None) -> Callable:
    """Decorator for custom rate limiting"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Custom rate limiting logic would go here
            # For now, rely on the global rate limiter
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def setup_security(app: Flask, api_keys: Optional[List[str]] = None) -> SecurityMiddleware:
    """Setup security middleware for Flask application"""
    security = SecurityMiddleware(app)
    
    if api_keys:
        for key in api_keys:
            security.api_auth.add_key(key)
    
    # Setup error handlers
    @app.errorhandler(Unauthorized)
    def handle_unauthorized(error):
        return jsonify({
            'success': False,
            'error': {
                'type': 'AuthenticationError',
                'message': 'Authentication failed',
                'code': 'UNAUTHORIZED'
            }
        }), 401
    
    @app.errorhandler(Forbidden)
    def handle_forbidden(error):
        return jsonify({
            'success': False,
            'error': {
                'type': 'AuthorizationError',
                'message': 'Access forbidden',
                'code': 'FORBIDDEN'
            }
        }), 403
    
    @app.errorhandler(TooManyRequests)
    def handle_rate_limit(error):
        return jsonify({
            'success': False,
            'error': {
                'type': 'RateLimitError',
                'message': 'Rate limit exceeded',
                'code': 'RATE_LIMIT_EXCEEDED'
            }
        }), 429
    
    return security
