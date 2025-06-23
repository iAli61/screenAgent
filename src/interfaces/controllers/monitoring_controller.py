"""
Monitoring Controller
Handles ROI monitoring-related API endpoints
"""
import json
from typing import Dict, Any, List
from datetime import datetime

from src.domain.interfaces.monitoring_service import IMonitoringService
from src.domain.interfaces.screenshot_service import IScreenshotService
from src.domain.entities.roi_region import ROIRegion
from src.domain.value_objects.coordinates import Rectangle


class MonitoringController:
    """Controller for monitoring operations"""
    
    def __init__(
        self,
        monitoring_service: IMonitoringService,
        screenshot_service: IScreenshotService
    ):
        self.monitoring_service = monitoring_service
        self.screenshot_service = screenshot_service
    
    async def get_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        try:
            # Get active sessions
            active_sessions = await self.monitoring_service.list_active_sessions()
            
            # Get screenshot count
            screenshots = await self.screenshot_service.list_screenshots()
            screenshot_count = len(screenshots)
            
            # Calculate last capture time
            last_capture = None
            if screenshots:
                last_capture = screenshots[0].timestamp.value.isoformat()
            
            status = {
                'monitoring_active': len(active_sessions) > 0,
                'active_sessions': len(active_sessions),
                'screenshot_count': screenshot_count,
                'last_capture': last_capture,
                'sessions': [
                    {
                        'id': session.id,
                        'roi_id': session.roi_region.id,
                        'status': session.status,
                        'start_time': session.start_time.isoformat(),
                        'screenshots_captured': session.screenshots_captured,
                        'changes_detected': session.changes_detected
                    }
                    for session in active_sessions
                ]
            }
            
            return {
                'success': True,
                'status': status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def start_monitoring(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start ROI monitoring"""
        try:
            # Parse ROI data
            roi_data = request_data.get('roi')
            if not roi_data or len(roi_data) != 4:
                return {
                    'success': False,
                    'error': 'Invalid ROI data. Expected [x, y, width, height]'
                }
            
            x, y, width, height = roi_data
            
            # Create ROI region
            roi_region = ROIRegion(
                id=f"roi_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=request_data.get('name', 'Manual ROI'),
                coordinates=Rectangle(x=x, y=y, width=width, height=height),
                description=request_data.get('description', ''),
                tags=request_data.get('tags', [])
            )
            
            # Parse monitoring parameters
            change_threshold = float(request_data.get('change_threshold', 20.0))
            check_interval = float(request_data.get('check_interval', 0.5))
            
            # Start monitoring
            session = await self.monitoring_service.start_monitoring(
                roi=roi_region,
                change_threshold=change_threshold,
                check_interval=check_interval
            )
            
            return {
                'success': True,
                'message': 'Monitoring started',
                'session': {
                    'id': session.id,
                    'roi_id': session.roi_region.id,
                    'status': session.status,
                    'start_time': session.start_time.isoformat(),
                    'change_threshold': session.change_threshold,
                    'check_interval': session.check_interval
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def stop_monitoring(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stop ROI monitoring"""
        try:
            session_id = request_data.get('session_id')
            
            if not session_id:
                # Stop all active sessions if no specific session provided
                active_sessions = await self.monitoring_service.list_active_sessions()
                stopped_count = 0
                
                for session in active_sessions:
                    success = await self.monitoring_service.stop_monitoring(session.id)
                    if success:
                        stopped_count += 1
                
                return {
                    'success': True,
                    'message': f'Stopped {stopped_count} monitoring sessions',
                    'stopped_count': stopped_count
                }
            else:
                # Stop specific session
                success = await self.monitoring_service.stop_monitoring(session_id)
                
                if success:
                    return {
                        'success': True,
                        'message': 'Monitoring stopped'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Session not found or could not be stopped'
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def pause_monitoring(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Pause ROI monitoring"""
        try:
            session_id = request_data.get('session_id')
            if not session_id:
                return {
                    'success': False,
                    'error': 'session_id required'
                }
            
            success = await self.monitoring_service.pause_monitoring(session_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Monitoring paused'
                }
            else:
                return {
                    'success': False,
                    'error': 'Session not found or could not be paused'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def resume_monitoring(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Resume ROI monitoring"""
        try:
            session_id = request_data.get('session_id')
            if not session_id:
                return {
                    'success': False,
                    'error': 'session_id required'
                }
            
            success = await self.monitoring_service.resume_monitoring(session_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Monitoring resumed'
                }
            else:
                return {
                    'success': False,
                    'error': 'Session not found or could not be resumed'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_monitoring_settings(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update monitoring settings"""
        try:
            session_id = request_data.get('session_id')
            if not session_id:
                return {
                    'success': False,
                    'error': 'session_id required'
                }
            
            change_threshold = request_data.get('change_threshold')
            check_interval = request_data.get('check_interval')
            
            if change_threshold is not None:
                change_threshold = float(change_threshold)
            if check_interval is not None:
                check_interval = float(check_interval)
            
            success = await self.monitoring_service.update_monitoring_config(
                session_id=session_id,
                change_threshold=change_threshold,
                check_interval=check_interval
            )
            
            if success:
                return {
                    'success': True,
                    'message': 'Monitoring settings updated'
                }
            else:
                return {
                    'success': False,
                    'error': 'Session not found or could not be updated'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_session_details(self, session_id: str) -> Dict[str, Any]:
        """Get details for a specific monitoring session"""
        try:
            session = await self.monitoring_service.get_monitoring_session(session_id)
            
            if not session:
                return {
                    'success': False,
                    'error': 'Session not found'
                }
            
            # Get session screenshots
            screenshots = await self.monitoring_service.get_session_screenshots(session_id)
            
            # Get change history
            changes = await self.monitoring_service.get_change_history(session_id)
            
            session_data = {
                'id': session.id,
                'roi_region': {
                    'id': session.roi_region.id,
                    'name': session.roi_region.name,
                    'coordinates': {
                        'x': session.roi_region.coordinates.x,
                        'y': session.roi_region.coordinates.y,
                        'width': session.roi_region.coordinates.width,
                        'height': session.roi_region.coordinates.height
                    },
                    'description': session.roi_region.description,
                    'tags': session.roi_region.tags
                },
                'status': session.status,
                'start_time': session.start_time.isoformat(),
                'end_time': session.end_time.isoformat() if session.end_time else None,
                'change_threshold': session.change_threshold,
                'check_interval': session.check_interval,
                'screenshots_captured': session.screenshots_captured,
                'changes_detected': session.changes_detected,
                'screenshots': [
                    {
                        'id': screenshot.id,
                        'timestamp': screenshot.timestamp.value.isoformat(),
                        'file_path': str(screenshot.file_path.path)
                    }
                    for screenshot in screenshots
                ],
                'change_history': changes
            }
            
            return {
                'success': True,
                'session': session_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_all_sessions(self, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all monitoring sessions"""
        try:
            # Parse query parameters
            limit = request_params.get('limit')
            offset = int(request_params.get('offset', 0))
            status_filter = request_params.get('status')
            
            if limit:
                limit = int(limit)
            
            # Get sessions based on filter
            if status_filter:
                # TODO: Implement status filtering when repository supports it
                # For now, get all sessions and filter
                all_sessions = await self.monitoring_service.list_active_sessions()
                sessions = [s for s in all_sessions if s.status == status_filter]
            else:
                sessions = await self.monitoring_service.list_active_sessions()
            
            # Apply pagination
            if limit:
                sessions = sessions[offset:offset + limit]
            
            session_data = []
            for session in sessions:
                session_data.append({
                    'id': session.id,
                    'roi_id': session.roi_region.id,
                    'roi_name': session.roi_region.name,
                    'status': session.status,
                    'start_time': session.start_time.isoformat(),
                    'end_time': session.end_time.isoformat() if session.end_time else None,
                    'screenshots_captured': session.screenshots_captured,
                    'changes_detected': session.changes_detected
                })
            
            return {
                'success': True,
                'sessions': session_data,
                'total_count': len(session_data),
                'offset': offset,
                'limit': limit
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def cleanup_old_sessions(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up old monitoring sessions"""
        try:
            max_age_days = int(request_data.get('max_age_days', 7))
            
            deleted_count = await self.monitoring_service.cleanup_completed_sessions(max_age_days)
            
            return {
                'success': True,
                'message': f'Cleaned up {deleted_count} old sessions',
                'deleted_count': deleted_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
