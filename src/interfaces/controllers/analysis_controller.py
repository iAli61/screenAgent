"""
Analysis Controller
Handles analysis-related API endpoints
"""
import json
from typing import Dict, Any, List
from datetime import datetime

from src.domain.interfaces.analysis_service import IAnalysisService
from src.domain.interfaces.screenshot_service import IScreenshotService


class AnalysisController:
    """Controller for analysis operations"""
    
    def __init__(
        self,
        analysis_service: IAnalysisService,
        screenshot_service: IScreenshotService
    ):
        self.analysis_service = analysis_service
        self.screenshot_service = screenshot_service
    
    async def analyze_screenshot(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single screenshot"""
        try:
            screenshot_id = request_data.get('screenshot_id')
            analysis_type = request_data.get('analysis_type', 'general')
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
            
            # Perform analysis based on type
            result = None
            
            if analysis_type == 'text_extraction':
                text_results = await self.analysis_service.extract_text(screenshot)
                result = {
                    'type': 'text_extraction',
                    'extracted_text': text_results,
                    'text_count': len(text_results)
                }
            
            elif analysis_type == 'object_detection':
                objects = await self.analysis_service.detect_objects(screenshot)
                result = {
                    'type': 'object_detection',
                    'detected_objects': objects,
                    'object_count': len(objects)
                }
            
            elif analysis_type == 'quality_analysis':
                quality = await self.analysis_service.analyze_image_quality(screenshot)
                result = {
                    'type': 'quality_analysis',
                    'quality_metrics': quality
                }
            
            elif analysis_type == 'comparison' and 'compare_with' in request_data:
                compare_screenshot_id = request_data['compare_with']
                compare_screenshot = await self.screenshot_service.get_screenshot(compare_screenshot_id)
                
                if not compare_screenshot:
                    return {
                        'success': False,
                        'error': 'Comparison screenshot not found'
                    }
                
                comparison_result = await self.analysis_service.compare_screenshots(
                    screenshot, compare_screenshot
                )
                
                result = {
                    'type': 'comparison',
                    'compared_with': compare_screenshot_id,
                    'similarity_score': comparison_result.results.get('similarity_score', 0),
                    'difference_score': comparison_result.results.get('difference_score', 0),
                    'has_changes': comparison_result.results.get('has_significant_changes', False)
                }
            
            else:
                # Default general analysis
                result = {
                    'type': 'general',
                    'message': f'Analysis completed for screenshot {screenshot_id}',
                    'custom_prompt': custom_prompt
                }
            
            return {
                'success': True,
                'analysis': {
                    'screenshot_id': screenshot_id,
                    'timestamp': datetime.now().isoformat(),
                    'result': result
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def compare_screenshots(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two screenshots"""
        try:
            screenshot1_id = request_data.get('screenshot1_id')
            screenshot2_id = request_data.get('screenshot2_id')
            threshold = float(request_data.get('threshold', 20.0))
            
            if not screenshot1_id or not screenshot2_id:
                return {
                    'success': False,
                    'error': 'Both screenshot1_id and screenshot2_id required'
                }
            
            # Get screenshots
            screenshot1 = await self.screenshot_service.get_screenshot(screenshot1_id)
            screenshot2 = await self.screenshot_service.get_screenshot(screenshot2_id)
            
            if not screenshot1:
                return {
                    'success': False,
                    'error': 'First screenshot not found'
                }
            
            if not screenshot2:
                return {
                    'success': False,
                    'error': 'Second screenshot not found'
                }
            
            # Perform comparison
            comparison_result = await self.analysis_service.compare_screenshots(
                screenshot1, screenshot2
            )
            
            # Check for changes
            changes_detected, change_score = await self.analysis_service.detect_changes(
                screenshot1, screenshot2, threshold=threshold
            )
            
            return {
                'success': True,
                'comparison': {
                    'screenshot1_id': screenshot1_id,
                    'screenshot2_id': screenshot2_id,
                    'threshold': threshold,
                    'changes_detected': changes_detected,
                    'change_score': change_score,
                    'similarity_score': comparison_result.results.get('similarity_score', 0),
                    'difference_score': comparison_result.results.get('difference_score', 0),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def batch_analyze(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform batch analysis on multiple screenshots"""
        try:
            screenshot_ids = request_data.get('screenshot_ids', [])
            analysis_types = request_data.get('analysis_types', ['general'])
            
            if not screenshot_ids:
                return {
                    'success': False,
                    'error': 'screenshot_ids required'
                }
            
            # Get screenshots
            screenshots = []
            for screenshot_id in screenshot_ids:
                screenshot = await self.screenshot_service.get_screenshot(screenshot_id)
                if screenshot:
                    screenshots.append(screenshot)
            
            if not screenshots:
                return {
                    'success': False,
                    'error': 'No valid screenshots found'
                }
            
            # Perform batch analysis
            analysis_results = await self.analysis_service.batch_analyze(
                screenshots, analysis_types
            )
            
            # Format results
            results = []
            for result in analysis_results:
                results.append({
                    'analysis_id': result.id,
                    'screenshot_id': result.screenshot_id,
                    'analysis_type': result.analysis_type,
                    'status': result.status,
                    'results': result.results,
                    'timestamp': result.timestamp.value.isoformat() if result.timestamp else None,
                    'error_message': result.error_message
                })
            
            return {
                'success': True,
                'batch_analysis': {
                    'requested_screenshots': len(screenshot_ids),
                    'processed_screenshots': len(screenshots),
                    'analysis_types': analysis_types,
                    'results': results,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def find_similar_screenshots(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find similar screenshots to a reference"""
        try:
            reference_id = request_data.get('reference_id')
            similarity_threshold = float(request_data.get('similarity_threshold', 0.8))
            limit = request_data.get('limit', 10)
            
            if not reference_id:
                return {
                    'success': False,
                    'error': 'reference_id required'
                }
            
            # Get reference screenshot
            reference_screenshot = await self.screenshot_service.get_screenshot(reference_id)
            if not reference_screenshot:
                return {
                    'success': False,
                    'error': 'Reference screenshot not found'
                }
            
            # Get all screenshots as candidates
            all_screenshots = await self.screenshot_service.list_screenshots()
            candidate_screenshots = [s for s in all_screenshots if s.id != reference_id]
            
            # Find similar screenshots
            similar_pairs = await self.analysis_service.find_similar_screenshots(
                reference_screenshot,
                candidate_screenshots,
                similarity_threshold
            )
            
            # Limit results
            if limit:
                similar_pairs = similar_pairs[:limit]
            
            # Format results
            similar_screenshots = []
            for screenshot, similarity_score in similar_pairs:
                similar_screenshots.append({
                    'screenshot_id': screenshot.id,
                    'similarity_score': similarity_score,
                    'timestamp': screenshot.timestamp.value.isoformat(),
                    'file_path': str(screenshot.file_path.path)
                })
            
            return {
                'success': True,
                'similar_screenshots': {
                    'reference_id': reference_id,
                    'similarity_threshold': similarity_threshold,
                    'found_count': len(similar_screenshots),
                    'similar_screenshots': similar_screenshots
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_thumbnail(self, request_data: Dict[str, Any]) -> bytes:
        """Generate thumbnail for a screenshot"""
        try:
            screenshot_id = request_data.get('screenshot_id')
            size = request_data.get('size', [200, 150])
            
            if not screenshot_id:
                return None
            
            # Get screenshot
            screenshot = await self.screenshot_service.get_screenshot(screenshot_id)
            if not screenshot:
                return None
            
            # Generate thumbnail
            thumbnail_data = await self.analysis_service.generate_thumbnail(
                screenshot, tuple(size)
            )
            
            return thumbnail_data
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            return None
    
    async def get_histogram(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get color histogram for a screenshot"""
        try:
            screenshot_id = request_data.get('screenshot_id')
            
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
            
            # Calculate histogram
            histogram = await self.analysis_service.calculate_histogram(screenshot)
            
            return {
                'success': True,
                'histogram': {
                    'screenshot_id': screenshot_id,
                    'data': histogram,
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
