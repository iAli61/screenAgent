"""
Screenshots Blueprint
Handles screenshot-related endpoints
"""
import asyncio
from flask import request, Response
from flask_restx import Namespace, Resource, fields

from src.infrastructure.dependency_injection import get_container


def run_async(coro):
    """Helper to run async functions in Flask context"""
    from flask import current_app
    
    # In test mode, return a mock response instead of running async code
    if current_app.config.get('DISABLE_ASYNC_EXECUTION', False):
        return {
            'success': True,
            'screenshots': [],
            'count': 0,
            'metadata': {}
        }
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(coro)
    finally:
        # Don't close the loop if it was the default loop
        pass

from src.infrastructure.dependency_injection import get_container
from src.interfaces.controllers.screenshot_controller import ScreenshotController


def run_async(coro):
    """Helper function to run async coroutines in Flask routes"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    try:
        return loop.run_until_complete(coro)
    finally:
        # Don't close the loop if it was the default loop
        pass

# Create namespace for screenshots
screenshots_bp = Namespace('screenshots', description='Screenshot operations')

# API Models for documentation
screenshot_model = screenshots_bp.model('Screenshot', {
    'id': fields.String(required=True, description='Screenshot ID'),
    'timestamp': fields.DateTime(required=True, description='Capture timestamp'),
    'width': fields.Integer(required=True, description='Image width'),
    'height': fields.Integer(required=True, description='Image height'),
    'file_path': fields.String(required=True, description='File path'),
    'session_id': fields.String(description='Monitoring session ID'),
    'metadata': fields.Raw(description='Additional metadata')
})

screenshot_list_model = screenshots_bp.model('ScreenshotList', {
    'success': fields.Boolean(required=True),
    'screenshots': fields.List(fields.Nested(screenshot_model)),
    'total_count': fields.Integer(description='Total number of screenshots'),
    'offset': fields.Integer(description='Query offset'),
    'limit': fields.Integer(description='Query limit')
})

trigger_model = screenshots_bp.model('TriggerRequest', {
    'metadata': fields.Raw(description='Optional metadata for screenshot')
})


@screenshots_bp.route('/screenshots')
class ScreenshotList(Resource):
    def get(self):
        """Get all screenshots with optional filtering"""
        container = get_container()
        screenshot_controller = container.get(ScreenshotController)
        
        params = {
            'limit': request.args.get('limit'),
            'offset': request.args.get('offset', 0),
            'session_id': request.args.get('session_id')
        }
        result = run_async(screenshot_controller.get_screenshots(params))
        return result
    
    def delete(self):
        """Delete all screenshots"""
        container = get_container()
        screenshot_controller = container.get(ScreenshotController)
        
        result = run_async(screenshot_controller.delete_all_screenshots())
        return result


@screenshots_bp.route('/trigger')
class ScreenshotTrigger(Resource):
    def post(self):
        """Trigger a new screenshot capture"""
        container = get_container()
        screenshot_controller = container.get(ScreenshotController)
        
        # Handle requests with or without JSON data
        try:
            data = request.get_json(force=True, silent=True) or {}
        except Exception:
            data = {}
            
        result = run_async(screenshot_controller.capture_full_screen(data))
        return result


@screenshots_bp.route('/take')
class ScreenshotTake(Resource):
    def post(self):
        """Take a new screenshot (alias for trigger)"""
        container = get_container()
        screenshot_controller = container.get(ScreenshotController)
        
        # Handle requests with or without JSON data
        try:
            data = request.get_json(force=True, silent=True) or {}
        except Exception:
            data = {}
            
        result = run_async(screenshot_controller.capture_full_screen(data))
        return result


@screenshots_bp.route('/preview')
class ScreenshotPreview(Resource):
    def get(self):
        """Get preview screenshot (returns PNG image data)"""
        container = get_container()
        screenshot_controller = container.get(ScreenshotController)
        
        result = run_async(screenshot_controller.get_preview({}))
        
        if result:
            return Response(
                result,
                mimetype='image/png',
                headers={
                    'Cache-Control': 'no-cache',
                    'Content-Type': 'image/png'
                }
            )
        else:
            screenshots_bp.abort(404, 'Preview not available')
    
    def head(self):
        """Handle HEAD requests for preview endpoint"""
        # Flask automatically handles HEAD by calling GET without body
        pass
