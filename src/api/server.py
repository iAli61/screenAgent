"""
Modern web server for ScreenAgent with improved API and UI
"""
import os
import json
import socket
import threading
import http.server
import socketserver
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

from ..core.config import Config
from ..core.screenshot_manager import ScreenshotManager
from ..core.roi_monitor import ROIMonitor
from .llm_api import LLMAnalyzer


class ScreenAgentServer:
    """Modern HTTP server for ScreenAgent"""
    
    def __init__(self, screenshot_manager: ScreenshotManager, roi_monitor: ROIMonitor, config: Config):
        self.screenshot_manager = screenshot_manager
        self.roi_monitor = roi_monitor
        self.config = config
        self.llm_analyzer = LLMAnalyzer(config)
        self.port = None
        self.httpd = None
        
        # Setup static file serving
        self.static_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'static'
        )
        self.templates_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'templates'
        )
    
    def find_available_port(self, start_port: int = None) -> Optional[int]:
        """Find an available port for the server"""
        if start_port is None:
            start_port = self.config.port
        
        max_attempts = self.config.max_port_attempts
        
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    result = s.connect_ex(('localhost', port))
                    if result != 0:  # Port is available
                        return port
            except Exception:
                continue
        
        print(f"❌ Could not find an available port in range {start_port}-{start_port + max_attempts - 1}")
        return None
    
    def start(self, port: int):
        """Start the HTTP server"""
        self.port = port
        
        # Create custom handler class with our data
        handler_class = self._create_handler_class()
        
        try:
            self.httpd = socketserver.TCPServer(("", port), handler_class)
            print(f"🌐 Web server started at http://localhost:{port}")
            self.httpd.serve_forever()
        except Exception as e:
            print(f"❌ Error starting server: {e}")
    
    def stop(self):
        """Stop the HTTP server"""
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            print("🌐 Web server stopped")
    
    def _create_handler_class(self):
        """Create a custom handler class with access to our managers"""
        screenshot_manager = self.screenshot_manager
        roi_monitor = self.roi_monitor
        config = self.config
        llm_analyzer = self.llm_analyzer
        static_dir = self.static_dir
        templates_dir = self.templates_dir
        
        class ScreenAgentHandler(http.server.BaseHTTPRequestHandler):
            
            def log_message(self, format, *args):
                """Override to reduce log noise"""
                pass
            
            def do_GET(self):
                """Handle GET requests"""
                path = urlparse(self.path).path
                
                if path == '/' or path == '/index.html':
                    self._serve_template('index.html')
                elif path == '/select_roi':
                    self._serve_roi_selection()
                elif path.startswith('/static/'):
                    self._serve_static_file(path[8:])  # Remove '/static/' prefix
                elif path.startswith('/screenshot/'):
                    self._serve_screenshot(path)
                elif path == '/temp_screenshot':
                    self._serve_temp_screenshot()
                elif path.startswith('/api/'):
                    self._handle_api_get(path)
                else:
                    self._send_404()
            
            def do_POST(self):
                """Handle POST requests"""
                path = urlparse(self.path).path
                
                if path.startswith('/api/'):
                    self._handle_api_post(path)
                elif path == '/set_roi':
                    self._handle_set_roi()
                else:
                    self._send_404()
            
            def do_DELETE(self):
                """Handle DELETE requests"""
                path = urlparse(self.path).path
                
                if path.startswith('/api/'):
                    self._handle_api_delete(path)
                else:
                    self._send_404()
            
            def _serve_template(self, template_name: str):
                """Serve an HTML template"""
                try:
                    template_path = os.path.join(templates_dir, template_name)
                    
                    if not os.path.exists(template_path):
                        self._send_404()
                        return
                    
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Basic template variable replacement
                    if template_name == 'index.html':
                        content = self._process_index_template(content)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
                    
                except Exception as e:
                    print(f"Error serving template {template_name}: {e}")
                    self._send_500()
            
            def _serve_roi_selection(self):
                """Serve the ROI selection page"""
                try:
                    # Take a full screenshot for ROI selection
                    print("📸 Taking screenshot for ROI selection...")
                    success = screenshot_manager.take_full_screenshot(save_to_temp=True)
                    if not success:
                        print("❌ Failed to take screenshot for ROI selection")
                    else:
                        print("✅ Screenshot taken successfully for ROI selection")
                    
                    template_path = os.path.join(templates_dir, 'select_roi.html')
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Replace template variables
                    current_roi = list(config.roi)
                    current_roi_str = f"({current_roi[0]}, {current_roi[1]}, {current_roi[2]}, {current_roi[3]})"
                    current_roi_js = json.dumps(current_roi)
                    
                    content = content.replace('{{ current_roi }}', current_roi_str)
                    content = content.replace('{{ current_roi_js }}', current_roi_js)
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(content.encode('utf-8'))
                    
                except Exception as e:
                    print(f"Error serving ROI selection: {e}")
                    import traceback
                    traceback.print_exc()
                    self._send_500()
            
            def _serve_static_file(self, file_path: str):
                """Serve static files (CSS, JS, images)"""
                try:
                    full_path = os.path.join(static_dir, file_path)
                    
                    if not os.path.exists(full_path):
                        self._send_404()
                        return
                    
                    # Security check - ensure file is within static directory
                    if not os.path.abspath(full_path).startswith(os.path.abspath(static_dir)):
                        self._send_404()
                        return
                    
                    # Determine content type
                    content_type = self._get_content_type(file_path)
                    
                    with open(full_path, 'rb') as f:
                        content = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-type', content_type)
                    self.send_header('Cache-Control', 'max-age=3600')  # Cache for 1 hour
                    self.end_headers()
                    self.wfile.write(content)
                    
                except Exception as e:
                    print(f"Error serving static file {file_path}: {e}")
                    self._send_404()
            
            def _serve_screenshot(self, path: str):
                """Serve a specific screenshot"""
                try:
                    # Extract screenshot index from path
                    index_str = path.split('/')[-1]
                    index = int(index_str)
                    
                    screenshot_data = screenshot_manager.get_screenshot_data(index)
                    if not screenshot_data:
                        self._send_404()
                        return
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.send_header('Cache-Control', 'max-age=86400')  # Cache for 24 hours
                    self.end_headers()
                    self.wfile.write(screenshot_data)
                    
                except (ValueError, IndexError):
                    self._send_404()
                except Exception as e:
                    print(f"Error serving screenshot: {e}")
                    self._send_500()
            
            def _serve_temp_screenshot(self):
                """Serve the temporary screenshot for ROI selection"""
                try:
                    temp_path = config.temp_screenshot_path
                    
                    if not os.path.exists(temp_path):
                        self._send_404()
                        return
                    
                    with open(temp_path, 'rb') as f:
                        content = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.send_header('Cache-Control', 'no-cache')
                    self.end_headers()
                    self.wfile.write(content)
                    
                except Exception as e:
                    print(f"Error serving temp screenshot: {e}")
                    self._send_404()
            
            def _handle_api_get(self, path: str):
                """Handle API GET requests"""
                if path == '/api/screenshots':
                    self._api_get_screenshots()
                elif path == '/api/status':
                    self._api_get_status()
                elif path == '/api/settings':
                    self._api_get_settings()
                elif path == '/api/roi':
                    self._api_get_roi()
                elif path == '/api/preview':
                    self._api_get_preview()
                else:
                    self._send_404()
            
            def _handle_api_post(self, path: str):
                """Handle API POST requests"""
                if path == '/api/trigger':
                    self._api_trigger_screenshot()
                elif path == '/api/analyze':
                    self._api_analyze_screenshot()
                elif path == '/api/settings':
                    self._api_save_settings()
                elif path == '/api/monitor/settings':
                    self._api_save_monitor_settings()
                elif path == '/api/monitoring/start':
                    self._api_start_monitoring()
                elif path == '/api/monitoring/stop':
                    self._api_stop_monitoring()
                else:
                    self._send_404()
            
            def _handle_api_delete(self, path: str):
                """Handle API DELETE requests"""
                if path == '/api/screenshots':
                    self._api_delete_all_screenshots()
                else:
                    self._send_404()
            
            def _handle_set_roi(self):
                """Handle ROI setting (legacy endpoint)"""
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length > 0:
                        post_data = self.rfile.read(content_length)
                        data = json.loads(post_data.decode('utf-8'))
                        
                        if 'roi' in data and len(data['roi']) == 4:
                            roi = tuple(map(int, data['roi']))
                            
                            # Validate ROI
                            left, top, right, bottom = roi
                            if left < right and top < bottom and right - left >= 10 and bottom - top >= 10:
                                config.roi = roi
                                self._send_json({'success': True, 'roi': list(roi)})
                                
                                # Clean up temp screenshot
                                temp_path = config.temp_screenshot_path
                                if os.path.exists(temp_path):
                                    try:
                                        os.remove(temp_path)
                                    except:
                                        pass
                                return
                    
                    self._send_json({'success': False, 'error': 'Invalid ROI'}, 400)
                    
                except Exception as e:
                    print(f"Error setting ROI: {e}")
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            # API endpoint implementations
            def _api_get_screenshots(self):
                """Get all screenshots"""
                try:
                    screenshots = screenshot_manager.get_all_screenshots()
                    status = roi_monitor.get_status()
                    
                    self._send_json({
                        'success': True,
                        'screenshots': screenshots,
                        'status': {
                            'active': status['active'],
                            'screenshot_count': len(screenshots),
                            'last_capture': screenshots[-1]['timestamp'] if screenshots else 'Never'
                        }
                    })
                except Exception as e:
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _api_get_status(self):
                """Get system status"""
                try:
                    roi_status = roi_monitor.get_status()
                    monitoring_status = screenshot_manager.is_monitoring()
                    screenshot_count = screenshot_manager.get_screenshot_count()
                    
                    status = {
                        'roi_monitor': roi_status,
                        'monitoring_active': monitoring_status,
                        'screenshot_count': screenshot_count,
                        'has_roi': bool(config.roi)
                    }
                    
                    self._send_json({'success': True, 'status': status})
                except Exception as e:
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _api_get_settings(self):
                """Get current settings"""
                try:
                    settings = {
                        'enabled': config.llm_enabled,
                        'model': config.llm_model,
                        'prompt': config.llm_prompt
                    }
                    self._send_json({'success': True, 'settings': settings})
                except Exception as e:
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _api_get_roi(self):
                """Get current ROI"""
                try:
                    self._send_json({'success': True, 'roi': list(config.roi)})
                except Exception as e:
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _api_get_preview(self):
                """Get preview screenshot"""
                try:
                    preview_data = screenshot_manager.take_screenshot(save_to_temp=False)
                    if preview_data:
                        self.send_response(200)
                        self.send_header('Content-type', 'image/png')
                        self.send_header('Cache-Control', 'no-cache')
                        self.end_headers()
                        self.wfile.write(preview_data)
                    else:
                        self._send_404()
                except Exception as e:
                    print(f"Error getting preview: {e}")
                    self._send_500()
            
            def _api_trigger_screenshot(self):
                """Trigger a manual screenshot"""
                try:
                    # Use screenshot manager instead of roi_monitor
                    roi = config.roi
                    screenshot = screenshot_manager.take_roi_screenshot(roi)
                    if screenshot:
                        # Add to screenshot manager's collection
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        screenshot_manager.add_screenshot(timestamp, screenshot, {
                            'manual': True,
                            'roi': roi
                        })
                        self._send_json({'success': True, 'message': 'Screenshot captured'})
                    else:
                        self._send_json({'success': False, 'error': 'Failed to capture screenshot'}, 500)
                except Exception as e:
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _api_analyze_screenshot(self):
                """Analyze a screenshot with AI"""
                try:
                    data = self._parse_json_body()
                    if not data:
                        self._send_json({'success': False, 'error': 'Invalid request data'}, 400)
                        return
                    
                    screenshot_idx = data.get('screenshot_idx')
                    custom_prompt = data.get('prompt')
                    
                    if screenshot_idx is None:
                        self._send_json({'success': False, 'error': 'screenshot_idx required'}, 400)
                        return
                    
                    # Get screenshot data
                    screenshot_data = screenshot_manager.get_screenshot_data(screenshot_idx)
                    if not screenshot_data:
                        self._send_json({'success': False, 'error': 'Screenshot not found'}, 404)
                        return
                    
                    # Analyze with LLM
                    response = llm_analyzer.analyze_image(screenshot_data, custom_prompt)
                    
                    if response:
                        # Store the response
                        screenshot_manager.set_llm_response(screenshot_idx, response)
                        self._send_json({'success': True, 'response': response})
                    else:
                        self._send_json({'success': False, 'error': 'LLM analysis failed'}, 500)
                    
                except Exception as e:
                    print(f"Error analyzing screenshot: {e}")
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _api_save_settings(self):
                """Save LLM settings"""
                try:
                    data = self._parse_json_body()
                    if not data:
                        self._send_json({'success': False, 'error': 'Invalid request data'}, 400)
                        return
                    
                    if 'enabled' in data:
                        config.llm_enabled = bool(data['enabled'])
                    if 'model' in data:
                        config.llm_model = str(data['model'])
                    if 'prompt' in data:
                        config.llm_prompt = str(data['prompt'])
                    
                    self._send_json({'success': True, 'message': 'Settings saved'})
                    
                except Exception as e:
                    print(f"Error saving settings: {e}")
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _api_save_monitor_settings(self):
                """Save monitoring settings"""
                try:
                    data = self._parse_json_body()
                    if not data:
                        self._send_json({'success': False, 'error': 'Invalid request data'}, 400)
                        return
                    
                    success = roi_monitor.update_settings(data)
                    
                    if success:
                        self._send_json({'success': True, 'message': 'Monitor settings saved'})
                    else:
                        self._send_json({'success': False, 'error': 'Failed to save settings'}, 500)
                    
                except Exception as e:
                    print(f"Error saving monitor settings: {e}")
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _api_delete_all_screenshots(self):
                """Delete all screenshots"""
                try:
                    success = screenshot_manager.clear_all_screenshots()
                    
                    if success:
                        self._send_json({'success': True, 'message': 'All screenshots deleted successfully'})
                    else:
                        self._send_json({'success': False, 'error': 'Failed to delete screenshots'}, 500)
                        
                except Exception as e:
                    print(f"Error deleting all screenshots: {e}")
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _api_start_monitoring(self):
                """Start ROI monitoring"""
                try:
                    if not config.roi:
                        self._send_json({'success': False, 'error': 'No ROI configured. Please select a region first.'}, 400)
                        return
                    
                    success = screenshot_manager.start_roi_monitoring(config.roi)
                    
                    if success:
                        self._send_json({'success': True, 'message': 'ROI monitoring started successfully'})
                    else:
                        self._send_json({'success': False, 'error': 'Failed to start monitoring'}, 500)
                        
                except Exception as e:
                    print(f"Error starting monitoring: {e}")
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _api_stop_monitoring(self):
                """Stop ROI monitoring"""
                try:
                    screenshot_manager.stop_roi_monitoring()
                    self._send_json({'success': True, 'message': 'ROI monitoring stopped successfully'})
                        
                except Exception as e:
                    print(f"Error stopping monitoring: {e}")
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            # Helper methods
            def _parse_json_body(self):
                """Parse JSON from request body"""
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    if content_length > 0:
                        post_data = self.rfile.read(content_length)
                        return json.loads(post_data.decode('utf-8'))
                except Exception:
                    pass
                return None
            
            def _send_json(self, data: Dict[str, Any], status: int = 200):
                """Send JSON response"""
                self.send_response(status)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode('utf-8'))
            
            def _send_404(self):
                """Send 404 response"""
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>404 Not Found</h1>')
            
            def _send_500(self):
                """Send 500 response"""
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>500 Internal Server Error</h1>')
            
            def _get_content_type(self, file_path: str) -> str:
                """Get content type for file"""
                ext = os.path.splitext(file_path)[1].lower()
                content_types = {
                    '.html': 'text/html; charset=utf-8',
                    '.css': 'text/css; charset=utf-8',
                    '.js': 'application/javascript; charset=utf-8',
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.svg': 'image/svg+xml',
                    '.ico': 'image/x-icon',
                    '.json': 'application/json; charset=utf-8'
                }
                return content_types.get(ext, 'application/octet-stream')
            
            def _process_index_template(self, content: str) -> str:
                """Process the index template with dynamic content"""
                # This is where you could add template processing
                # For now, just return as-is
                return content
        
        return ScreenAgentHandler
