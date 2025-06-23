"""
Modern web server for ScreenAgent with clean architecture
Uses dependency injection and controllers for all operations
"""
import os
import json
import socket
import threading
import http.server
import socketserver
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

from ..infrastructure.dependency_injection.container import get_container
from ..interfaces.controllers import (
    ScreenshotController,
    MonitoringController,
    AnalysisController,
    ConfigurationController
)


class ScreenAgentServer:
    """Modern HTTP server for ScreenAgent with clean architecture"""
    
    def __init__(self):
        """Initialize server with clean architecture dependency injection"""
        # Get services from DI container
        try:
            container = get_container()
            
            # Get services from container
            from ..domain.interfaces.screenshot_service import IScreenshotService
            from ..domain.interfaces.monitoring_service import IMonitoringService
            from ..domain.interfaces.analysis_service import IAnalysisService
            from ..domain.repositories.configuration_repository import IConfigurationRepository
            
            screenshot_service = container.get(IScreenshotService)
            monitoring_service = container.get(IMonitoringService)
            analysis_service = container.get(IAnalysisService)
            configuration_repository = container.get(IConfigurationRepository)
            
            # Initialize controllers
            self.screenshot_controller = ScreenshotController(screenshot_service, analysis_service)
            self.monitoring_controller = MonitoringController(monitoring_service, screenshot_service)
            self.analysis_controller = AnalysisController(analysis_service, screenshot_service)
            self.configuration_controller = ConfigurationController(configuration_repository)
            
            # Get configuration from repository
            config_dict = asyncio.run(configuration_repository.get_all_config())
            self.config = config_dict
            
        except Exception as e:
            print(f"❌ Failed to initialize clean architecture: {e}")
            raise Exception(f"Server initialization failed: {e}")
        
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
            start_port = self.config.get("server", {}).get("port", 8000)
        
        max_attempts = self.config.get("server", {}).get("max_port_attempts", 10)
        
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
        """Create a custom handler class with access to controllers"""
        # Clean architecture controllers
        screenshot_controller = self.screenshot_controller
        monitoring_controller = self.monitoring_controller
        analysis_controller = self.analysis_controller
        configuration_controller = self.configuration_controller
        config = self.config
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
                    # Take a full screenshot for ROI selection using controller
                    print("📸 Taking screenshot for ROI selection...")
                    result = self._call_controller_async(
                        screenshot_controller.capture_full_screen,
                        {'save_to_temp': True}
                    )
                    
                    if result.get('success'):
                        print("✅ Screenshot taken successfully for ROI selection")
                    else:
                        print("❌ Failed to take screenshot for ROI selection")
                    
                    template_path = os.path.join(templates_dir, 'select_roi.html')
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Get current ROI from configuration
                    config_result = self._call_controller_async(
                        configuration_controller.get_configuration, {}
                    )
                    current_roi = config_result.get('configuration', {}).get('roi', [0, 0, 100, 100])
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
                    
                    # If it's a number, treat it as legacy index
                    # Otherwise, treat it as screenshot ID
                    try:
                        index = int(index_str)
                        # Get all screenshots to find by index
                        result = self._call_controller_async(
                            screenshot_controller.get_screenshots, {}
                        )
                        
                        if not result.get('success'):
                            self._send_404()
                            return
                        
                        screenshots = result.get('screenshots', [])
                        if 0 <= index < len(screenshots):
                            screenshot_id = screenshots[index]['id']
                        else:
                            self._send_404()
                            return
                    except ValueError:
                        # Treat as screenshot ID
                        screenshot_id = index_str
                    
                    # Get screenshot data using ID
                    result = self._call_controller_async(
                        screenshot_controller.get_screenshot_by_id,
                        screenshot_id
                    )
                    
                    if not result.get('success'):
                        self._send_404()
                        return
                    
                    screenshot_data = result.get('screenshot', {}).get('data')
                    if not screenshot_data:
                        self._send_404()
                        return
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.send_header('Cache-Control', 'max-age=86400')  # Cache for 24 hours
                    self.end_headers()
                    self.wfile.write(screenshot_data)
                    
                except Exception as e:
                    print(f"Error serving screenshot: {e}")
                    self._send_500()
            
            def _serve_temp_screenshot(self):
                """Serve the temporary screenshot for ROI selection"""
                try:
                    # Get temp screenshot path from configuration
                    config_result = self._call_controller_async(
                        configuration_controller.get_configuration, {}
                    )
                    temp_path = config_result.get('configuration', {}).get('temp_screenshot_path')
                    
                    if not temp_path or not os.path.exists(temp_path):
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
                """Handle API GET requests using controllers"""
                try:
                    if path == '/api/screenshots':
                        response = self._call_controller_async(
                            screenshot_controller.get_screenshots, {}
                        )
                        self._send_json(response)
                    elif path == '/api/status':
                        response = self._call_controller_async(
                            monitoring_controller.get_status
                        )
                        self._send_json(response)
                    elif path == '/api/settings':
                        response = self._call_controller_async(
                            configuration_controller.get_configuration, {}
                        )
                        self._send_json(response)
                    elif path == '/api/roi':
                        # Get ROI from configuration
                        config_result = self._call_controller_async(
                            configuration_controller.get_configuration, {}
                        )
                        roi = config_result.get('configuration', {}).get('roi', [0, 0, 100, 100])
                        self._send_json({'success': True, 'roi': roi})
                    elif path == '/api/preview':
                        self._api_get_preview()
                    else:
                        self._send_404()
                except Exception as e:
                    print(f"Error in API GET handler: {e}")
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _handle_api_post(self, path: str):
                """Handle API POST requests using controllers"""
                try:
                    data = self._parse_json_body()
                    
                    if path == '/api/trigger':
                        response = self._call_controller_async(
                            screenshot_controller.capture_full_screen, data or {}
                        )
                        self._send_json(response)
                    elif path == '/api/analyze':
                        response = self._call_controller_async(
                            analysis_controller.analyze_screenshot, data or {}
                        )
                        self._send_json(response)
                    elif path == '/api/settings':
                        response = self._call_controller_async(
                            configuration_controller.update_configuration, 
                            {'configuration': data} if data else {}
                        )
                        self._send_json(response)
                    elif path == '/api/monitor/settings':
                        # Legacy monitoring settings - delegate to monitoring controller
                        response = self._call_controller_async(
                            monitoring_controller.update_settings, data or {}
                        )
                        self._send_json(response)
                    elif path == '/api/monitoring/start':
                        response = self._call_controller_async(
                            monitoring_controller.start_monitoring, data or {}
                        )
                        self._send_json(response)
                    elif path == '/api/monitoring/stop':
                        response = self._call_controller_async(
                            monitoring_controller.stop_monitoring, data or {}
                        )
                        self._send_json(response)
                    else:
                        self._send_404()
                except Exception as e:
                    print(f"Error in API POST handler: {e}")
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            def _handle_api_delete(self, path: str):
                """Handle API DELETE requests using controllers"""
                try:
                    if path == '/api/screenshots':
                        response = self._call_controller_async(
                            screenshot_controller.delete_all_screenshots
                        )
                        self._send_json(response)
                    else:
                        self._send_404()
                except Exception as e:
                    print(f"Error in API DELETE handler: {e}")
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
            # Helper methods
            def _call_controller_async(self, controller_method, data=None):
                """Call an async controller method synchronously"""
                import asyncio
                try:
                    # Create a new event loop for this thread if none exists
                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    
                    # Run the async method with or without data
                    if data is not None:
                        return loop.run_until_complete(controller_method(data))
                    else:
                        return loop.run_until_complete(controller_method())
                except Exception as e:
                    print(f"Error calling controller method: {e}")
                    return {'success': False, 'error': str(e)}
            
            def _api_get_preview(self):
                """Get preview screenshot using controller"""
                try:
                    result = self._call_controller_async(
                        screenshot_controller.get_preview,
                        {}
                    )
                    
                    if result:
                        self.send_response(200)
                        self.send_header('Content-type', 'image/png')
                        self.send_header('Cache-Control', 'no-cache')
                        self.end_headers()
                        self.wfile.write(result)
                    else:
                        self._send_404()
                except Exception as e:
                    print(f"Error getting preview: {e}")
                    self._send_500()
            
            # Helper method for handling ROI updates
            def _handle_set_roi(self):
                """Handle ROI setting using configuration controller"""
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
                                # Update ROI using configuration controller
                                result = self._call_controller_async(
                                    configuration_controller.update_configuration,
                                    {'configuration': {'roi': list(roi)}}
                                )
                                
                                if result.get('success'):
                                    self._send_json({'success': True, 'roi': list(roi)})
                                    
                                    # Clean up temp screenshot
                                    config_result = self._call_controller_async(
                                        configuration_controller.get_configuration, {}
                                    )
                                    temp_path = config_result.get('configuration', {}).get('temp_screenshot_path')
                                    if temp_path and os.path.exists(temp_path):
                                        try:
                                            os.remove(temp_path)
                                        except:
                                            pass
                                    return
                                else:
                                    self._send_json({'success': False, 'error': 'Failed to update ROI'}, 500)
                                    return
                    
                    self._send_json({'success': False, 'error': 'Invalid ROI'}, 400)
                    
                except Exception as e:
                    print(f"Error setting ROI: {e}")
                    self._send_json({'success': False, 'error': str(e)}, 500)
            
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
