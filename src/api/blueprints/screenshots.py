"""
Screenshots Blueprint
Handles screenshot-related endpoints
"""
import asyncio
from flask import request, Response, abort
from flask_restx import Namespace, Resource, fields

from src.infrastructure.dependency_injection import get_container


def run_async(coro):
    """Helper to run async functions in Flask context"""
    from flask import current_app
    
    # In test mode, return a mock response instead of running async code
    if current_app.config.get('DISABLE_ASYNC_EXECUTION', False):
        print("DEBUG: DISABLE_ASYNC_EXECUTION is True, returning mock data")
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
        print(f"DEBUG: About to run coroutine: {coro}")
        result = loop.run_until_complete(coro)
        print(f"DEBUG: Coroutine result type: {type(result)}, size: {len(result) if isinstance(result, bytes) else 'N/A'}")
        return result
    except Exception as e:
        print(f"DEBUG: Exception in run_async: {e}")
        raise e
    finally:
        # Don't close the loop if it was the default loop
        pass

from src.infrastructure.dependency_injection import get_container
from src.interfaces.controllers.screenshot_controller import ScreenshotController

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


@screenshots_bp.route('/take')
class ScreenshotTake(Resource):
    def post(self):
        """Take a new screenshot, optionally using a Region of Interest (ROI)"""
        container = get_container()
        screenshot_controller = container.get(ScreenshotController)
        
        # Handle requests with or without JSON data
        try:
            data = request.get_json(force=True, silent=True) or {}
        except Exception:
            data = {}
        
        # Check if ROI parameters are provided
        if 'roi' in data and isinstance(data['roi'], dict):
            roi_data = data['roi']
            required_fields = ['x', 'y', 'width', 'height']
            
            # Validate ROI parameters
            if all(field in roi_data for field in required_fields):
                try:
                    # Capture screenshot with ROI
                    print(f"DEBUG: Capturing screenshot with ROI: {roi_data}")
                    result = run_async(screenshot_controller.capture_roi_region(roi_data))
                    return result
                except Exception as e:
                    print(f"DEBUG: Error capturing ROI screenshot: {e}")
                    return {"success": False, "error": str(e)}, 500
            else:
                missing = [field for field in required_fields if field not in roi_data]
                return {"success": False, "error": f"Missing ROI fields: {', '.join(missing)}"}, 400
        
        # Default: capture full screen if no ROI specified
        print("DEBUG: Capturing full screen screenshot")
        result = run_async(screenshot_controller.capture_full_screen(data))
        return result


@screenshots_bp.route('/preview')
class ScreenshotPreview(Resource):
    def get(self):
        """Get preview screenshot (returns PNG image data)"""
        try:
            container = get_container()
            screenshot_controller = container.get(ScreenshotController)
            
            result = run_async(screenshot_controller.get_preview({}))
            
            if result and isinstance(result, bytes):
                return Response(
                    result,
                    mimetype='image/png',
                    headers={
                        'Cache-Control': 'no-cache',
                        'Content-Type': 'image/png'
                    }
                )
            else:
                # Return error information for debugging
                return {
                    'error': 'Preview generation failed',
                    'result_type': type(result).__name__ if result else 'None',
                    'result_size': len(result) if isinstance(result, bytes) else 'N/A'
                }, 500
        except Exception as e:
            return {
                'error': 'Preview endpoint exception',
                'message': str(e),
                'type': type(e).__name__
            }, 500
    
    def head(self):
        """Handle HEAD requests for preview endpoint"""
        # Flask automatically handles HEAD by calling GET without body
        pass


@screenshots_bp.route('/<string:screenshot_id>')
class ScreenshotImage(Resource):
    def get(self, screenshot_id):
        """Get individual screenshot image by ID"""
        container = get_container()
        screenshot_controller = container.get(ScreenshotController)
        
        try:
            # Get screenshot image data
            image_data = run_async(screenshot_controller.get_screenshot_image(screenshot_id))
            
            if image_data:
                return Response(
                    image_data,
                    mimetype='image/png',
                    headers={
                        'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
                        'Content-Type': 'image/png'
                    }
                )
            else:
                abort(404, description=f"Screenshot {screenshot_id} not found")
        except Exception as e:
            abort(500, description=f"Error retrieving screenshot: {str(e)}")

    def delete(self, screenshot_id):
        """Delete individual screenshot by ID"""
        container = get_container()
        screenshot_controller = container.get(ScreenshotController)
        
        try:
            result = run_async(screenshot_controller.delete_screenshot(screenshot_id))
            return result
        except Exception as e:
            abort(500, description=f"Error deleting screenshot: {str(e)}")

    def head(self, screenshot_id):
        """Handle HEAD requests for individual screenshots"""
        # Flask automatically handles HEAD by calling GET without body
        pass
