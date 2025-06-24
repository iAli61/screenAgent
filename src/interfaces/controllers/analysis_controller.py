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
            provider = request_data.get('provider')
            model = request_data.get('model')
            
            if not screenshot_id:
                return {
                    'success': False,
                    'error': 'Missing required parameter: screenshot_id',
                    'error_code': 'MISSING_SCREENSHOT_ID',
                    'details': 'Please provide a valid screenshot_id to analyze'
                }
            
            # Get screenshot
            screenshot = await self.screenshot_service.get_screenshot(screenshot_id)
            if not screenshot:
                return {
                    'success': False,
                    'error': f'Screenshot not found: {screenshot_id}',
                    'error_code': 'SCREENSHOT_NOT_FOUND',
                    'details': f'No screenshot exists with ID "{screenshot_id}". Please verify the screenshot ID and try again.'
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
                        'error': f'Comparison screenshot not found: {compare_screenshot_id}',
                        'error_code': 'COMPARISON_SCREENSHOT_NOT_FOUND',
                        'details': f'No screenshot exists with ID "{compare_screenshot_id}" for comparison. Please verify the screenshot ID and try again.'
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
                # Default general analysis with AI
                from src.api.llm_api import LLMAnalyzer
                
                # Initialize LLM analyzer
                llm_analyzer = LLMAnalyzer({
                    'llm_enabled': True,
                    'llm_model': 'gpt-4o'
                })
                
                analysis_text = None
                failure_reason = None
                llm_status = "disabled"
                
                if llm_analyzer.is_available():
                    llm_status = "available"
                    try:
                        # Get screenshot image data
                        screenshot_path = screenshot.file_path.path
                        if screenshot_path:
                            with open(screenshot_path, 'rb') as f:
                                image_data = f.read()
                            
                            print(f"Attempting LLM analysis for screenshot {screenshot_id} using provider: {provider or 'auto'}, model: {model or 'default'}...")
                            
                            # Perform AI analysis
                            analysis_text = llm_analyzer.analyze_image(
                                image_data, 
                                custom_prompt or "Analyze this screenshot and describe what you see in detail.",
                                provider=provider,
                                model=model
                            )
                            
                            if analysis_text:
                                print(f"✅ LLM analysis successful for screenshot {screenshot_id}")
                                llm_status = "success"
                            else:
                                print(f"⚠️ LLM analysis returned empty result for screenshot {screenshot_id}")
                                failure_reason = "LLM returned empty/null response - this could indicate API quota limits, content filtering, or processing errors"
                                llm_status = "empty_response"
                        else:
                            failure_reason = "Screenshot file path is None or empty"
                            llm_status = "invalid_file_path"
                            
                    except FileNotFoundError:
                        failure_reason = f"Screenshot file not found: {screenshot_path}"
                        llm_status = "file_not_found"
                        print(f"❌ {failure_reason}")
                    except PermissionError:
                        failure_reason = f"Permission denied accessing screenshot file: {screenshot_path}"
                        llm_status = "permission_denied"
                        print(f"❌ {failure_reason}")
                    except Exception as e:
                        failure_reason = f"LLM analysis failed with exception: {type(e).__name__}: {str(e)}"
                        llm_status = "exception"
                        print(f"❌ {failure_reason}")
                else:
                    failure_reason = "LLM analyzer is not available - check API keys and configuration"
                    print(f"⚠️ {failure_reason}")
                
                # Provide informative fallback analysis with diagnostic information
                if not analysis_text:
                    diagnostic_info = {
                        'llm_status': llm_status,
                        'failure_reason': failure_reason,
                        'available_providers': llm_analyzer.get_available_providers(),
                        'requested_provider': provider,
                        'requested_model': model,
                        'llm_enabled': llm_analyzer.llm_enabled,
                        'screenshot_path': str(screenshot.file_path.path) if screenshot.file_path.path else 'None'
                    }
                    
                    analysis_text = f"""Screenshot Analysis Fallback for {screenshot_id}

❌ LLM Analysis Failed
Status: {llm_status}
Reason: {failure_reason or 'Unknown'}
Requested Provider: {provider or 'auto'}
Requested Model: {model or 'default'}
Available Providers: {', '.join(diagnostic_info['available_providers']) or 'None'}
LLM Enabled: {diagnostic_info['llm_enabled']}

📋 Basic Analysis:
This screenshot appears to be a captured image from the system. Without AI analysis, only basic metadata is available.
Custom prompt was: '{custom_prompt or 'default analysis'}'

🔧 Troubleshooting:
- Check API keys (AZURE_AI_API_KEY, GITHUB_MODEL_TOKEN, OPENAI_API_KEY)
- Verify network connectivity
- Check API quota limits
- Ensure screenshot file exists and is accessible
- Verify provider and model parameters

For full AI-powered analysis, please resolve the LLM configuration issues."""
                
                result = {
                    'type': 'general',
                    'analysis': analysis_text,
                    'custom_prompt': custom_prompt,
                    'provider': provider,
                    'model': model,
                    'llm_enabled': llm_analyzer.llm_enabled,
                    'llm_status': llm_status,
                    'available_providers': llm_analyzer.get_available_providers(),
                    'failure_reason': failure_reason if not analysis_text or llm_status != 'success' else None
                }
            
            return {
                'success': True,
                'analysis_id': f'analysis_{screenshot_id}_{int(datetime.now().timestamp())}',
                'result': result,
                'confidence': 0.9 if analysis_text and llm_status == 'success' else 0.5,
                'timestamp': datetime.now().isoformat(),
                'processing_time': 1.0,  # Placeholder
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'analysis_id': None,
                'result': None,
                'confidence': None,
                'timestamp': datetime.now().isoformat(),
                'processing_time': None,
                'error': f'Analysis failed: {str(e)}',
                'error_code': 'ANALYSIS_PROCESSING_ERROR',
                'details': f'An error occurred while processing the screenshot analysis: {type(e).__name__}: {str(e)}'
            }
    
    async def compare_screenshots(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two screenshots"""
        try:
            screenshot1_id = request_data.get('screenshot1_id')
            screenshot2_id = request_data.get('screenshot2_id')
            threshold = float(request_data.get('threshold', 20.0))
            
            if not screenshot1_id or not screenshot2_id:
                missing_params = []
                if not screenshot1_id:
                    missing_params.append('screenshot1_id')
                if not screenshot2_id:
                    missing_params.append('screenshot2_id')
                
                return {
                    'success': False,
                    'error': f'Missing required parameters: {", ".join(missing_params)}',
                    'error_code': 'MISSING_REQUIRED_PARAMETERS',
                    'details': 'Both screenshot1_id and screenshot2_id are required for comparison'
                }
            
            # Get screenshots
            screenshot1 = await self.screenshot_service.get_screenshot(screenshot1_id)
            screenshot2 = await self.screenshot_service.get_screenshot(screenshot2_id)
            
            if not screenshot1:
                return {
                    'success': False,
                    'error': f'First screenshot not found: {screenshot1_id}',
                    'error_code': 'FIRST_SCREENSHOT_NOT_FOUND',
                    'details': f'No screenshot exists with ID "{screenshot1_id}" for comparison'
                }
            
            if not screenshot2:
                return {
                    'success': False,
                    'error': f'Second screenshot not found: {screenshot2_id}',
                    'error_code': 'SECOND_SCREENSHOT_NOT_FOUND',
                    'details': f'No screenshot exists with ID "{screenshot2_id}" for comparison'
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
                'error': f'Comparison failed: {str(e)}',
                'error_code': 'COMPARISON_PROCESSING_ERROR',
                'details': f'An error occurred while comparing screenshots: {type(e).__name__}: {str(e)}'
            }
    
    async def batch_analyze(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform batch analysis on multiple screenshots"""
        try:
            screenshot_ids = request_data.get('screenshot_ids', [])
            analysis_types = request_data.get('analysis_types', ['general'])
            
            if not screenshot_ids:
                return {
                    'success': False,
                    'error': 'Missing required parameter: screenshot_ids',
                    'error_code': 'MISSING_SCREENSHOT_IDS',
                    'details': 'Please provide a list of screenshot_ids to analyze in batch'
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
                    'error': f'No valid screenshots found from provided IDs: {screenshot_ids}',
                    'error_code': 'NO_VALID_SCREENSHOTS',
                    'details': f'None of the provided screenshot IDs ({len(screenshot_ids)} total) could be found in the system'
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
                'error': f'Batch analysis failed: {str(e)}',
                'error_code': 'BATCH_ANALYSIS_ERROR',
                'details': f'An error occurred during batch analysis: {type(e).__name__}: {str(e)}'
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
                    'error': 'Missing required parameter: reference_id',
                    'error_code': 'MISSING_REFERENCE_ID',
                    'details': 'Please provide a reference_id to find similar screenshots'
                }
            
            # Get reference screenshot
            reference_screenshot = await self.screenshot_service.get_screenshot(reference_id)
            if not reference_screenshot:
                return {
                    'success': False,
                    'error': f'Reference screenshot not found: {reference_id}',
                    'error_code': 'REFERENCE_SCREENSHOT_NOT_FOUND',
                    'details': f'No screenshot exists with ID "{reference_id}" to use as reference'
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
                'error': f'Similar screenshots search failed: {str(e)}',
                'error_code': 'SIMILAR_SCREENSHOTS_ERROR',
                'details': f'An error occurred while searching for similar screenshots: {type(e).__name__}: {str(e)}'
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
                    'error': 'Missing required parameter: screenshot_id',
                    'error_code': 'MISSING_SCREENSHOT_ID',
                    'details': 'Please provide a valid screenshot_id to calculate histogram'
                }
            
            # Get screenshot
            screenshot = await self.screenshot_service.get_screenshot(screenshot_id)
            if not screenshot:
                return {
                    'success': False,
                    'error': f'Screenshot not found: {screenshot_id}',
                    'error_code': 'SCREENSHOT_NOT_FOUND',
                    'details': f'No screenshot exists with ID "{screenshot_id}" for histogram calculation'
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
                'error': f'Histogram calculation failed: {str(e)}',
                'error_code': 'HISTOGRAM_CALCULATION_ERROR',
                'details': f'An error occurred while calculating histogram: {type(e).__name__}: {str(e)}'
            }
