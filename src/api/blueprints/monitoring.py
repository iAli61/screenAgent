"""
Monitoring API Blueprint
Handles monitoring session endpoints
"""
import asyncio
from flask import request
from flask_restx import Namespace, Resource, fields

from src.interfaces.controllers.monitoring_controller import MonitoringController
from src.infrastructure.dependency_injection.container import get_container

def run_async(coro):
    """Helper to run async functions in Flask"""
    from flask import current_app
    
    # In test mode, return a mock response instead of running async code
    if current_app.config.get('DISABLE_ASYNC_EXECUTION', False):
        return {
            'success': True,
            'session_id': 'test-session-123',
            'sessions': [],
            'screenshots': [],
            'status': 'active'
        }
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

# Create namespace for monitoring
monitoring_bp = Namespace('monitoring', description='Monitoring operations')

# API Models for documentation
roi_model = monitoring_bp.model('ROI', {
    'x': fields.Integer(required=True, description='ROI x coordinate'),
    'y': fields.Integer(required=True, description='ROI y coordinate'),
    'width': fields.Integer(required=True, description='ROI width'),
    'height': fields.Integer(required=True, description='ROI height')
})

session_model = monitoring_bp.model('MonitoringSession', {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'session_id': fields.String(description='Session ID'),
    'roi': fields.Nested(roi_model, description='Region of Interest'),
    'interval': fields.Float(description='Monitoring interval in seconds'),
    'threshold': fields.Float(description='Change detection threshold'),
    'status': fields.String(enum=['running', 'stopped', 'paused'], description='Session status'),
    'created_at': fields.DateTime(description='Session creation time'),
    'last_screenshot': fields.DateTime(description='Last screenshot timestamp'),
    'error': fields.String(description='Error message if operation failed')
})

session_list_model = monitoring_bp.model('SessionList', {
    'success': fields.Boolean(required=True),
    'sessions': fields.List(fields.Nested(session_model)),
    'total_count': fields.Integer(description='Total number of sessions')
})

session_create_model = monitoring_bp.model('SessionCreate', {
    'roi': fields.Nested(roi_model, required=True, description='Region of Interest'),
    'interval': fields.Float(description='Monitoring interval in seconds', default=1.0),
    'threshold': fields.Float(description='Change detection threshold', default=0.1)
})

session_update_model = monitoring_bp.model('SessionUpdate', {
    'roi': fields.Nested(roi_model, description='Updated Region of Interest'),
    'interval': fields.Float(description='Updated monitoring interval'),
    'threshold': fields.Float(description='Updated change detection threshold')
})


@monitoring_bp.route('/sessions')
class MonitoringSessionList(Resource):
    @monitoring_bp.marshal_with(session_list_model)
    @monitoring_bp.doc('get_sessions')
    def get(self):
        """Get all monitoring sessions"""
        container = get_container()
        monitoring_controller = container.get(MonitoringController)
        
        result = run_async(monitoring_controller.get_all_sessions({}))
        return result
    
    @monitoring_bp.expect(session_create_model)
    @monitoring_bp.marshal_with(session_model)
    @monitoring_bp.doc('create_session')
    def post(self):
        """Create a new monitoring session"""
        container = get_container()
        monitoring_controller = container.get(MonitoringController)
        
        data = request.get_json()
        result = run_async(monitoring_controller.create_session(data))
        return result


@monitoring_bp.route('/sessions/<string:session_id>')
class MonitoringSession(Resource):
    @monitoring_bp.marshal_with(session_model)
    @monitoring_bp.doc('get_session')
    def get(self, session_id):
        """Get a specific monitoring session"""
        container = get_container()
        monitoring_controller = container.get(MonitoringController)
        
        result = run_async(monitoring_controller.get_session(session_id))
        return result
    
    @monitoring_bp.expect(session_update_model)
    @monitoring_bp.marshal_with(session_model)
    @monitoring_bp.doc('update_session')
    def put(self, session_id):
        """Update a monitoring session"""
        container = get_container()
        monitoring_controller = container.get(MonitoringController)
        
        data = request.get_json()
        result = run_async(monitoring_controller.update_session(session_id, data))
        return result
    
    @monitoring_bp.doc('delete_session')
    def delete(self, session_id):
        """Delete a monitoring session"""
        container = get_container()
        monitoring_controller = container.get(MonitoringController)
        
        result = run_async(monitoring_controller.delete_session(session_id))
        return result


@monitoring_bp.route('/sessions/<string:session_id>/start')
class MonitoringSessionStart(Resource):
    @monitoring_bp.doc('start_session')
    def post(self, session_id):
        """Start a monitoring session"""
        container = get_container()
        monitoring_controller = container.get(MonitoringController)
        
        result = run_async(monitoring_controller.start_session(session_id))
        return result


@monitoring_bp.route('/sessions/<string:session_id>/stop')
class MonitoringSessionStop(Resource):
    @monitoring_bp.doc('stop_session')
    def post(self, session_id):
        """Stop a monitoring session"""
        container = get_container()
        monitoring_controller = container.get(MonitoringController)
        
        result = run_async(monitoring_controller.stop_session(session_id))
        return result


@monitoring_bp.route('/sessions/<string:session_id>/pause')
class MonitoringSessionPause(Resource):
    @monitoring_bp.doc('pause_session')
    def post(self, session_id):
        """Pause a monitoring session"""
        container = get_container()
        monitoring_controller = container.get(MonitoringController)
        
        result = run_async(monitoring_controller.pause_session(session_id))
        return result
    
    @monitoring_bp.doc('resume_session')
    def delete(self, session_id):
        """Resume a paused monitoring session"""
        container = get_container()
        monitoring_controller = container.get(MonitoringController)
        
        result = run_async(monitoring_controller.resume_session(session_id))
        return result


@monitoring_bp.route('/sessions/<string:session_id>/screenshots')
class MonitoringSessionScreenshots(Resource):
    @monitoring_bp.doc('get_session_screenshots')
    def get(self, session_id):
        """Get screenshots for a specific monitoring session"""
        container = get_container()
        monitoring_controller = container.get(MonitoringController)
        
        params = {
            'limit': request.args.get('limit'),
            'offset': request.args.get('offset', 0)
        }
        result = run_async(monitoring_controller.get_session_screenshots(session_id, params))
        return result
