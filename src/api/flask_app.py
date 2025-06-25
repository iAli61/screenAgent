"""
Flask Application Factory
Main Flask application setup with Flask-RESTX (Swagger), CORS, and dependency injection
"""
from flask import Flask
from flask_restx import Api
from flask_cors import CORS

from src.infrastructure.dependency_injection import get_container, setup_container


def create_app(config=None) -> Flask:
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    if config:
        app.config.update(config)
    else:
        # Basic configuration for now
        app.config.update({
            'DEBUG': True,
            'TESTING': False,
            'SECRET_KEY': 'dev-secret-key-change-in-production',
            'LOG_LEVEL': 'INFO',
            'SLOW_REQUEST_THRESHOLD': 2.0
        })
    
    # Setup Flask-RESTX API with Swagger documentation
    api = Api(
        app,
        version='1.0',
        title='ScreenAgent API',
        description='AI-powered screenshot monitoring and analysis API',
        doc='/docs/',  # Swagger UI endpoint
        prefix='/api'
    )
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-API-Key", "X-Request-ID"]
        }
    })
    
    # Setup middleware (but not for testing to avoid conflicts)
    if not app.config.get('TESTING', False):
        from src.api.middleware.error_handler import setup_error_handling
        from src.api.middleware.validation import setup_validation_error_handler
        from src.api.middleware.security import setup_security
        
        setup_error_handling(app, api)
        setup_validation_error_handler(app)
        setup_security(app)
    
    # Create API models
    from src.api.models.swagger_models import create_api_models
    models = create_api_models(api)
    
    # Register blueprints
    from src.api.blueprints.screenshots import screenshots_bp
    from src.api.blueprints.monitoring import monitoring_bp
    from src.api.blueprints.configuration import config_bp
    from src.api.blueprints.analysis import analysis_bp
    from src.api.blueprints.models import models_bp
    from src.api.blueprints.prompts import prompts_bp
    
    api.add_namespace(screenshots_bp, path='/screenshots')
    api.add_namespace(monitoring_bp, path='/monitoring') 
    api.add_namespace(config_bp, path='/config')
    api.add_namespace(analysis_bp, path='/analysis')
    api.add_namespace(models_bp, path='/models')
    api.add_namespace(prompts_bp, path='/prompts')
    
    # Setup dependency injection using the existing DI system
    from src.utils.platform_detection import is_wsl, is_windows, is_linux_with_display
    
    # Detect platform for configuration
    if is_wsl():
        platform_name = "wsl"
    elif is_windows():
        platform_name = "windows"
    elif is_linux_with_display():
        platform_name = "linux"
    else:
        platform_name = "unknown"
    
    config_dict = {
        "storage": {
            "type": "file",
            "base_path": "screenshots"
        },
        "monitoring": {
            "default_strategy": "threshold",
            "threshold": 20
        },
        "capture": {
            "platform": platform_name,
            "wsl_enabled": is_wsl()
        },
        "server": {
            "port": 8000,
            "max_port_attempts": 10
        },
        "config_file": "config/screen_agent_config.json"
    }
    
    setup_container(config_dict)
    # DI container is now available globally via get_container()
    
    # Override Flask-RESTX error handler to fix Response object bug
    @api.errorhandler(Exception)
    def handle_flask_restx_error(error):
        """Custom error handler to fix Flask-RESTX Response object bug"""
        from werkzeug.exceptions import HTTPException
        
        if isinstance(error, HTTPException):
            return {
                'success': False,
                'error': {
                    'type': 'HTTPError',
                    'message': error.description or str(error),
                    'code': f'HTTP_{error.code}',
                    'status_code': error.code
                },
                'request_id': 'unknown'
            }, error.code
        else:
            return {
                'success': False,
                'error': {
                    'type': type(error).__name__,
                    'message': str(error),
                    'code': 'INTERNAL_ERROR'
                },
                'request_id': 'unknown'
            }, 500
    
    return app


def create_production_app():
    """Create Flask app for production deployment"""
    return create_app({
        'DEBUG': False,
        'TESTING': False,
        'SECRET_KEY': 'production-secret-key',
        'LOG_LEVEL': 'WARNING'
    })
    app.config['DEBUG'] = False
    return app


if __name__ == '__main__':
    # Development server
    app = create_app()
    app.run(host='127.0.0.1', port=8000, debug=True)
