"""
Swagger API Models
Centralized API model definitions for documentation
"""
from flask_restx import fields

def create_api_models(api):
    """Create and register all API models with Flask-RESTX"""
    
    # Common models
    error_model = api.model('Error', {
        'type': fields.String(required=True, description='Error type'),
        'message': fields.String(required=True, description='Error message'),
        'code': fields.String(required=True, description='Error code'),
        'field': fields.String(description='Field that caused the error'),
        'details': fields.Raw(description='Additional error details')
    })
    
    api_response_model = api.model('ApiResponse', {
        'success': fields.Boolean(required=True, description='Request success status'),
        'message': fields.String(description='Response message'),
        'error': fields.Nested(error_model, description='Error details if success=false'),
        'request_id': fields.String(description='Request tracking ID')
    })
    
    # ROI (Region of Interest) model
    roi_model = api.model('ROI', {
        'x': fields.Integer(required=True, description='X coordinate', min=0),
        'y': fields.Integer(required=True, description='Y coordinate', min=0),
        'width': fields.Integer(required=True, description='Width in pixels', min=1),
        'height': fields.Integer(required=True, description='Height in pixels', min=1)
    })
    
    # Screenshot models
    screenshot_metadata_model = api.model('ScreenshotMetadata', {
        'capture_method': fields.String(description='Screenshot capture method'),
        'display_info': fields.Raw(description='Display information'),
        'user_agent': fields.String(description='User agent if applicable'),
        'custom_data': fields.Raw(description='Custom metadata')
    })
    
    screenshot_model = api.model('Screenshot', {
        'id': fields.String(required=True, description='Unique screenshot ID'),
        'timestamp': fields.DateTime(required=True, description='Capture timestamp'),
        'width': fields.Integer(required=True, description='Image width in pixels'),
        'height': fields.Integer(required=True, description='Image height in pixels'),
        'file_path': fields.String(required=True, description='Screenshot file path'),
        'file_size': fields.Integer(description='File size in bytes'),
        'format': fields.String(description='Image format (PNG, JPEG, etc.)'),
        'session_id': fields.String(description='Associated monitoring session ID'),
        'roi': fields.Nested(roi_model, description='Region of interest if captured'),
        'metadata': fields.Nested(screenshot_metadata_model, description='Additional metadata')
    })
    
    screenshot_list_model = api.model('ScreenshotList', {
        'success': fields.Boolean(required=True),
        'screenshots': fields.List(fields.Nested(screenshot_model)),
        'total_count': fields.Integer(description='Total number of screenshots'),
        'offset': fields.Integer(description='Query offset'),
        'limit': fields.Integer(description='Query limit'),
        'has_more': fields.Boolean(description='Whether more results are available')
    })
    
    screenshot_trigger_model = api.model('ScreenshotTrigger', {
        'roi': fields.Nested(roi_model, description='Optional region of interest'),
        'metadata': fields.Nested(screenshot_metadata_model, description='Optional metadata'),
        'quality': fields.Integer(description='Image quality (1-100)', min=1, max=100, default=90),
        'format': fields.String(description='Output format', enum=['PNG', 'JPEG'], default='PNG')
    })
    
    # Monitoring models
    monitoring_session_model = api.model('MonitoringSession', {
        'session_id': fields.String(required=True, description='Unique session ID'),
        'roi': fields.Nested(roi_model, required=True, description='Monitored region'),
        'interval': fields.Float(description='Monitoring interval in seconds', min=0.1, max=3600, default=1.0),
        'threshold': fields.Float(description='Change detection threshold (0-1)', min=0.0, max=1.0, default=0.1),
        'status': fields.String(enum=['running', 'stopped', 'paused'], description='Session status'),
        'created_at': fields.DateTime(description='Session creation timestamp'),
        'updated_at': fields.DateTime(description='Last update timestamp'),
        'last_screenshot': fields.DateTime(description='Last screenshot timestamp'),
        'screenshot_count': fields.Integer(description='Number of screenshots captured'),
        'change_count': fields.Integer(description='Number of changes detected'),
        'metadata': fields.Raw(description='Session metadata')
    })
    
    monitoring_session_create_model = api.model('MonitoringSessionCreate', {
        'roi': fields.Nested(roi_model, required=True, description='Region to monitor'),
        'interval': fields.Float(description='Monitoring interval in seconds', min=0.1, max=3600, default=1.0),
        'threshold': fields.Float(description='Change detection threshold (0-1)', min=0.0, max=1.0, default=0.1),
        'metadata': fields.Raw(description='Optional session metadata')
    })
    
    monitoring_session_update_model = api.model('MonitoringSessionUpdate', {
        'roi': fields.Nested(roi_model, description='Updated region to monitor'),
        'interval': fields.Float(description='Updated monitoring interval', min=0.1, max=3600),
        'threshold': fields.Float(description='Updated change detection threshold', min=0.0, max=1.0),
        'metadata': fields.Raw(description='Updated session metadata')
    })
    
    monitoring_session_list_model = api.model('MonitoringSessionList', {
        'success': fields.Boolean(required=True),
        'sessions': fields.List(fields.Nested(monitoring_session_model)),
        'total_count': fields.Integer(description='Total number of sessions'),
        'active_count': fields.Integer(description='Number of active sessions'),
        'paused_count': fields.Integer(description='Number of paused sessions')
    })
    
    # Analysis models
    analysis_request_model = api.model('AnalysisRequest', {
        'screenshot_id': fields.String(description='Screenshot ID to analyze'),
        'roi': fields.Nested(roi_model, description='Region of interest for analysis'),
        'analysis_type': fields.String(
            enum=['general', 'text', 'ui_elements', 'changes', 'custom'],
            description='Type of analysis to perform',
            default='general'
        ),
        'prompt': fields.String(description='Custom analysis prompt', max_length=1000),
        'compare_with': fields.String(description='Screenshot ID to compare with'),
        'options': fields.Raw(description='Analysis-specific options')
    })
    
    analysis_result_model = api.model('AnalysisResult', {
        'id': fields.String(required=True, description='Unique analysis ID'),
        'screenshot_id': fields.String(required=True, description='Analyzed screenshot ID'),
        'analysis_type': fields.String(required=True, description='Type of analysis performed'),
        'result': fields.Raw(required=True, description='Analysis results'),
        'confidence': fields.Float(description='Confidence score (0-1)', min=0.0, max=1.0),
        'timestamp': fields.DateTime(required=True, description='Analysis timestamp'),
        'processing_time': fields.Float(description='Processing time in seconds'),
        'model_version': fields.String(description='AI model version used'),
        'tokens_used': fields.Integer(description='Number of tokens consumed'),
        'metadata': fields.Raw(description='Additional analysis metadata')
    })
    
    analysis_list_model = api.model('AnalysisList', {
        'success': fields.Boolean(required=True),
        'analyses': fields.List(fields.Nested(analysis_result_model)),
        'total_count': fields.Integer(description='Total number of analyses'),
        'offset': fields.Integer(description='Query offset'),
        'limit': fields.Integer(description='Query limit')
    })
    
    comparison_result_model = api.model('ComparisonResult', {
        'id': fields.String(required=True, description='Unique comparison ID'),
        'screenshot1_id': fields.String(required=True, description='First screenshot ID'),
        'screenshot2_id': fields.String(required=True, description='Second screenshot ID'),
        'similarity_score': fields.Float(description='Overall similarity score (0-1)', min=0.0, max=1.0),
        'differences': fields.Raw(description='Detected differences'),
        'change_areas': fields.List(fields.Nested(roi_model), description='Areas with changes'),
        'change_percentage': fields.Float(description='Percentage of image that changed'),
        'timestamp': fields.DateTime(required=True, description='Comparison timestamp'),
        'processing_time': fields.Float(description='Processing time in seconds')
    })
    
    # Configuration models
    config_section_model = api.model('ConfigSection', {
        'screenshot': fields.Raw(description='Screenshot configuration'),
        'monitoring': fields.Raw(description='Monitoring configuration'),
        'server': fields.Raw(description='Server configuration'),
        'logging': fields.Raw(description='Logging configuration'),
        'security': fields.Raw(description='Security configuration'),
        'ai': fields.Raw(description='AI/Analysis configuration')
    })
    
    config_update_model = api.model('ConfigUpdate', {
        'section': fields.String(required=True, description='Configuration section to update'),
        'data': fields.Raw(required=True, description='Configuration data')
    })
    
    config_backup_model = api.model('ConfigBackup', {
        'id': fields.String(required=True, description='Backup ID'),
        'timestamp': fields.DateTime(required=True, description='Backup timestamp'),
        'description': fields.String(description='Backup description'),
        'size': fields.Integer(description='Backup size in bytes'),
        'checksum': fields.String(description='Backup checksum')
    })
    
    config_backup_list_model = api.model('ConfigBackupList', {
        'success': fields.Boolean(required=True),
        'backups': fields.List(fields.Nested(config_backup_model)),
        'total_count': fields.Integer(description='Total number of backups')
    })
    
    # System status models
    system_status_model = api.model('SystemStatus', {
        'status': fields.String(enum=['healthy', 'degraded', 'unhealthy'], description='Overall system status'),
        'timestamp': fields.DateTime(required=True, description='Status check timestamp'),
        'uptime': fields.Float(description='System uptime in seconds'),
        'version': fields.String(description='Application version'),
        'environment': fields.String(description='Environment (dev, staging, prod)'),
        'components': fields.Raw(description='Component-specific status'),
        'metrics': fields.Raw(description='System metrics'),
        'active_sessions': fields.Integer(description='Number of active monitoring sessions'),
        'total_screenshots': fields.Integer(description='Total screenshots captured'),
        'disk_usage': fields.Raw(description='Disk usage information'),
        'memory_usage': fields.Raw(description='Memory usage information')
    })
    
    health_check_model = api.model('HealthCheck', {
        'status': fields.String(enum=['ok', 'error'], description='Health status'),
        'timestamp': fields.DateTime(required=True, description='Health check timestamp'),
        'checks': fields.Raw(description='Individual health checks'),
        'response_time': fields.Float(description='Health check response time in seconds')
    })
    
    # Return dictionary of all models for easy access
    return {
        # Common
        'error': error_model,
        'api_response': api_response_model,
        'roi': roi_model,
        
        # Screenshots
        'screenshot': screenshot_model,
        'screenshot_list': screenshot_list_model,
        'screenshot_trigger': screenshot_trigger_model,
        'screenshot_metadata': screenshot_metadata_model,
        
        # Monitoring
        'monitoring_session': monitoring_session_model,
        'monitoring_session_create': monitoring_session_create_model,
        'monitoring_session_update': monitoring_session_update_model,
        'monitoring_session_list': monitoring_session_list_model,
        
        # Analysis
        'analysis_request': analysis_request_model,
        'analysis_result': analysis_result_model,
        'analysis_list': analysis_list_model,
        'comparison_result': comparison_result_model,
        
        # Configuration
        'config_section': config_section_model,
        'config_update': config_update_model,
        'config_backup': config_backup_model,
        'config_backup_list': config_backup_list_model,
        
        # System
        'system_status': system_status_model,
        'health_check': health_check_model
    }
