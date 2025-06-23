"""
Screenshot Controller
Handles screenshot-related API endpoints
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime

from src.domain.interfaces.screenshot_service import IScreenshotService
from src.domain.interfaces.analysis_service import IAnalysisService
from src.domain.value_objects.coordinates import Rectangle


class ScreenshotController:
    """Controller for screenshot operations"""
    
    def __init__(
        self,
        screenshot_service: IScreenshotService,
        analysis_service: IAnalysisService
    ):
        self.screenshot_service = screenshot_service
        self.analysis_service = analysis_service
    
    async def get_screenshots(self, request_params: Dict[str, Any]) -> Dict[str, Any]:
        """Get all screenshots with optional filtering"""
        try:
            # Parse query parameters
            limit = request_params.get('limit')
            offset = int(request_params.get('offset', 0))
            session_id = request_params.get('session_id')
            
            if limit:
                limit = int(limit)
            
            # Get screenshots from service
            screenshots = await self.screenshot_service.list_screenshots(
                session_id=session_id,
                limit=limit,
                offset=offset
            )
            
            # Convert to API response format
            screenshot_data = []
            for screenshot in screenshots:
                screenshot_data.append({
                    'id': screenshot.id,
                    'timestamp': screenshot.timestamp.value.isoformat(),
                    'width': screenshot.width,
                    'height': screenshot.height,
                    'format': screenshot.format,
                    'size_bytes': screenshot.size_bytes,
                    'file_path': str(screenshot.file_path.path),
                    'metadata': screenshot.metadata
                })
            
            return {
                'success': True,
                'screenshots': screenshot_data,
                'total_count': len(screenshot_data),
                'offset': offset,
                'limit': limit
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_screenshot_by_id(self, screenshot_id: str) -> Dict[str, Any]:
        """Get a specific screenshot by ID"""
        try:
            screenshot = await self.screenshot_service.get_screenshot(screenshot_id)
            
            if not screenshot:
                return {
                    'success': False,
                    'error': 'Screenshot not found'
                }
            
            return {
                'success': True,
                'screenshot': {
                    'id': screenshot.id,
                    'timestamp': screenshot.timestamp.value.isoformat(),
                    'width': screenshot.width,
                    'height': screenshot.height,
                    'format': screenshot.format,
                    'size_bytes': screenshot.size_bytes,
                    'file_path': str(screenshot.file_path.path),
                    'metadata': screenshot.metadata
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def capture_full_screen(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Capture a full screen screenshot"""
        try:
            monitor_id = request_data.get('monitor_id')
            metadata = request_data.get('metadata', {})
            metadata['manual'] = True
            metadata['capture_method'] = 'full_screen'
            
            screenshot = await self.screenshot_service.capture_full_screen(
                monitor_id=monitor_id,
                metadata=metadata
            )
            
            return {
                'success': True,
                'message': 'Screenshot captured',
                'screenshot': {
                    'id': screenshot.id,
                    'timestamp': screenshot.timestamp.value.isoformat(),
                    'width': screenshot.width,
                    'height': screenshot.height
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def capture_region(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Capture a screenshot of a specific region"""
        try:
            region_data = request_data.get('region')
            if not region_data or len(region_data) != 4:
                return {
                    'success': False,
                    'error': 'Invalid region data. Expected [x, y, width, height]'
                }
            
            x, y, width, height = region_data
            region = Rectangle(x=x, y=y, width=width, height=height)
            
            monitor_id = request_data.get('monitor_id')
            metadata = request_data.get('metadata', {})
            metadata['manual'] = True
            metadata['capture_method'] = 'region'
            metadata['region'] = region_data
            
            screenshot = await self.screenshot_service.capture_region(
                region=region,
                monitor_id=monitor_id,
                metadata=metadata
            )
            
            return {
                'success': True,
                'message': 'Region screenshot captured',
                'screenshot': {
                    'id': screenshot.id,
                    'timestamp': screenshot.timestamp.value.isoformat(),
                    'width': screenshot.width,
                    'height': screenshot.height
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def delete_screenshot(self, screenshot_id: str) -> Dict[str, Any]:
        """Delete a specific screenshot"""
        try:
            success = await self.screenshot_service.delete_screenshot(screenshot_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Screenshot deleted'
                }
            else:
                return {
                    'success': False,
                    'error': 'Screenshot not found or could not be deleted'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def delete_all_screenshots(self) -> Dict[str, Any]:
        """Delete all screenshots"""
        try:
            # Get all screenshots first
            screenshots = await self.screenshot_service.list_screenshots()
            
            deleted_count = 0
            for screenshot in screenshots:
                success = await self.screenshot_service.delete_screenshot(screenshot.id)
                if success:
                    deleted_count += 1
            
            return {
                'success': True,
                'message': f'Deleted {deleted_count} screenshots',
                'deleted_count': deleted_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_screenshot(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a screenshot with AI"""
        try:
            screenshot_id = request_data.get('screenshot_id')
            custom_prompt = request_data.get('prompt')
            
            if not screenshot_id:
                return {
                    'success': False,
                    'error': 'screenshot_id required'
                }
            
            # Get screenshot
            screenshot = await self.screenshot_service.get_screenshot(screenshot_id)
            if not screenshot:
                return {
                    'success': False,
                    'error': 'Screenshot not found'
                }
            
            # TODO: Implement AI analysis when analysis service is complete
            # For now, return placeholder response
            response = f"Analysis of screenshot {screenshot_id}"
            if custom_prompt:
                response += f" with prompt: {custom_prompt}"
            
            return {
                'success': True,
                'analysis': {
                    'screenshot_id': screenshot_id,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_preview(self, request_params: Dict[str, Any]) -> Optional[bytes]:
        """Get a preview screenshot (returns raw image data)"""
        try:
            # Capture a temporary screenshot for preview
            metadata = {'preview': True, 'temporary': True}
            screenshot = await self.screenshot_service.capture_full_screen(metadata=metadata)
            
            # TODO: Return actual image data when file service is implemented
            # For now, return None to indicate no preview available
            return None
            
        except Exception as e:
            print(f"Error generating preview: {e}")
            return None
    
    async def cleanup_old_screenshots(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean up old screenshots"""
        try:
            max_age_days = request_data.get('max_age_days', 30)
            max_count = request_data.get('max_count')
            
            deleted_count = await self.screenshot_service.cleanup_old_screenshots(
                max_age_days=max_age_days,
                max_count=max_count
            )
            
            return {
                'success': True,
                'message': f'Cleaned up {deleted_count} old screenshots',
                'deleted_count': deleted_count
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
