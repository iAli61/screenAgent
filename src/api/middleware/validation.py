"""
Validation Middleware
Request validation and data sanitization
"""
import re
from typing import Dict, Any, List, Optional, Union, Callable
from functools import wraps
from flask import request, jsonify
from werkzeug.exceptions import BadRequest
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error"""
    def __init__(self, message: str, field: str = None, code: str = None):
        self.message = message
        self.field = field
        self.code = code or 'VALIDATION_ERROR'
        super().__init__(message)


class RequestValidator:
    """Request validation utilities"""
    
    @staticmethod
    def validate_json_required():
        """Decorator to ensure request has JSON content"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if not request.is_json:
                    raise ValidationError("Request must contain JSON data", code="INVALID_CONTENT_TYPE")
                return f(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def validate_schema(schema: Dict[str, Any]):
        """Decorator to validate request JSON against schema"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if not request.is_json:
                    raise ValidationError("Request must contain JSON data", code="INVALID_CONTENT_TYPE")
                
                data = request.get_json()
                RequestValidator._validate_data_against_schema(data, schema)
                return f(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def validate_params(params_schema: Dict[str, Any]):
        """Decorator to validate query parameters"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                RequestValidator._validate_query_params(request.args, params_schema)
                return f(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def _validate_data_against_schema(data: Dict[str, Any], schema: Dict[str, Any]):
        """Validate data against schema definition"""
        if not isinstance(data, dict):
            raise ValidationError("Data must be a JSON object", code="INVALID_DATA_TYPE")
        
        # Check required fields
        required_fields = schema.get('required', [])
        for field in required_fields:
            if field not in data:
                raise ValidationError(f"Missing required field: {field}", field=field, code="MISSING_FIELD")
        
        # Validate each field
        properties = schema.get('properties', {})
        for field_name, field_schema in properties.items():
            if field_name in data:
                RequestValidator._validate_field(data[field_name], field_schema, field_name)
    
    @staticmethod
    def _validate_field(value: Any, field_schema: Dict[str, Any], field_name: str):
        """Validate individual field against schema"""
        field_type = field_schema.get('type')
        
        # Type validation
        if field_type == 'string' and not isinstance(value, str):
            raise ValidationError(f"Field {field_name} must be a string", field=field_name, code="INVALID_TYPE")
        elif field_type == 'integer' and not isinstance(value, int):
            raise ValidationError(f"Field {field_name} must be an integer", field=field_name, code="INVALID_TYPE")
        elif field_type == 'number' and not isinstance(value, (int, float)):
            raise ValidationError(f"Field {field_name} must be a number", field=field_name, code="INVALID_TYPE")
        elif field_type == 'boolean' and not isinstance(value, bool):
            raise ValidationError(f"Field {field_name} must be a boolean", field=field_name, code="INVALID_TYPE")
        elif field_type == 'array' and not isinstance(value, list):
            raise ValidationError(f"Field {field_name} must be an array", field=field_name, code="INVALID_TYPE")
        elif field_type == 'object' and not isinstance(value, dict):
            raise ValidationError(f"Field {field_name} must be an object", field=field_name, code="INVALID_TYPE")
        
        # String validations
        if field_type == 'string':
            min_length = field_schema.get('minLength')
            max_length = field_schema.get('maxLength')
            pattern = field_schema.get('pattern')
            
            if min_length is not None and len(value) < min_length:
                raise ValidationError(
                    f"Field {field_name} must be at least {min_length} characters long",
                    field=field_name, code="MIN_LENGTH"
                )
            
            if max_length is not None and len(value) > max_length:
                raise ValidationError(
                    f"Field {field_name} must be at most {max_length} characters long",
                    field=field_name, code="MAX_LENGTH"
                )
            
            if pattern and not re.match(pattern, value):
                raise ValidationError(
                    f"Field {field_name} does not match required pattern",
                    field=field_name, code="INVALID_PATTERN"
                )
        
        # Number validations
        if field_type in ['integer', 'number']:
            minimum = field_schema.get('minimum')
            maximum = field_schema.get('maximum')
            
            if minimum is not None and value < minimum:
                raise ValidationError(
                    f"Field {field_name} must be at least {minimum}",
                    field=field_name, code="MIN_VALUE"
                )
            
            if maximum is not None and value > maximum:
                raise ValidationError(
                    f"Field {field_name} must be at most {maximum}",
                    field=field_name, code="MAX_VALUE"
                )
        
        # Enum validation
        enum_values = field_schema.get('enum')
        if enum_values and value not in enum_values:
            raise ValidationError(
                f"Field {field_name} must be one of: {', '.join(map(str, enum_values))}",
                field=field_name, code="INVALID_ENUM"
            )
    
    @staticmethod
    def _validate_query_params(params: Dict[str, str], params_schema: Dict[str, Any]):
        """Validate query parameters"""
        for param_name, param_schema in params_schema.items():
            if param_name in params:
                param_value = params.get(param_name)
                
                # Type conversion and validation
                param_type = param_schema.get('type', 'string')
                try:
                    if param_type == 'integer':
                        param_value = int(param_value)
                    elif param_type == 'number':
                        param_value = float(param_value)
                    elif param_type == 'boolean':
                        param_value = param_value.lower() in ('true', '1', 'yes', 'on')
                    
                    # Validate converted value
                    RequestValidator._validate_field(param_value, param_schema, param_name)
                    
                except ValueError:
                    raise ValidationError(
                        f"Query parameter {param_name} has invalid type",
                        field=param_name, code="INVALID_PARAM_TYPE"
                    )
            elif param_schema.get('required', False):
                raise ValidationError(
                    f"Missing required query parameter: {param_name}",
                    field=param_name, code="MISSING_PARAM"
                )


class DataSanitizer:
    """Data sanitization utilities"""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove HTML tags and escape special characters"""
        if not isinstance(text, str):
            return text
        
        # Simple HTML tag removal (for more complex cases, use bleach library)
        html_pattern = re.compile(r'<[^>]+>')
        return html_pattern.sub('', text)
    
    @staticmethod
    def sanitize_sql(text: str) -> str:
        """Basic SQL injection prevention"""
        if not isinstance(text, str):
            return text
        
        # Remove common SQL injection patterns
        dangerous_patterns = [
            r"('|(\\')|(;)|(\\;)|(\|)|(\*)|(\%)|(\[))",
            r"(union|select|insert|delete|update|drop|create|alter|exec|execute)",
            r"(script|javascript|vbscript|onload|onerror|onclick)"
        ]
        
        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        if not isinstance(filename, str):
            return filename
        
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\.\.', '', filename)  # Remove path traversal
        filename = filename.strip('. ')  # Remove leading/trailing dots and spaces
        
        return filename[:255]  # Limit length


def setup_validation_error_handler(app):
    """Setup validation error handler for Flask app"""
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        logger.warning(f"Validation error: {error.message}")
        
        return jsonify({
            'success': False,
            'error': {
                'type': 'ValidationError',
                'message': error.message,
                'code': error.code,
                'field': error.field
            }
        }), 400


# Common validation schemas
SCREENSHOT_SCHEMAS = {
    'trigger': {
        'type': 'object',
        'properties': {
            'metadata': {'type': 'object'},
            'roi': {
                'type': 'object',
                'properties': {
                    'x': {'type': 'integer', 'minimum': 0},
                    'y': {'type': 'integer', 'minimum': 0},
                    'width': {'type': 'integer', 'minimum': 1},
                    'height': {'type': 'integer', 'minimum': 1}
                },
                'required': ['x', 'y', 'width', 'height']
            }
        }
    }
}

MONITORING_SCHEMAS = {
    'create_session': {
        'type': 'object',
        'properties': {
            'roi': {
                'type': 'object',
                'properties': {
                    'x': {'type': 'integer', 'minimum': 0},
                    'y': {'type': 'integer', 'minimum': 0},
                    'width': {'type': 'integer', 'minimum': 1},
                    'height': {'type': 'integer', 'minimum': 1}
                },
                'required': ['x', 'y', 'width', 'height']
            },
            'interval': {'type': 'number', 'minimum': 0.1, 'maximum': 3600},
            'threshold': {'type': 'number', 'minimum': 0.0, 'maximum': 1.0}
        },
        'required': ['roi']
    }
}

ANALYSIS_SCHEMAS = {
    'analyze': {
        'type': 'object',
        'properties': {
            'screenshot_id': {'type': 'string', 'minLength': 1},
            'analysis_type': {
                'type': 'string',
                'enum': ['general', 'text', 'ui_elements', 'changes']
            },
            'prompt': {'type': 'string', 'maxLength': 1000},
            'roi': {
                'type': 'object',
                'properties': {
                    'x': {'type': 'integer', 'minimum': 0},
                    'y': {'type': 'integer', 'minimum': 0},
                    'width': {'type': 'integer', 'minimum': 1},
                    'height': {'type': 'integer', 'minimum': 1}
                }
            }
        }
    }
}
