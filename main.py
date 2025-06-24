"""
ScreenAgent Core Application
Refactored with clean architecture and dependency injection
"""
import os
import sys
import threading
import signal
from typing import Optional

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# For module loading
sys.path.append('src')
sys.path.append('src/core')
sys.path.append('src/core/config')

from src.infrastructure.dependency_injection import get_container, setup_container
from src.domain.interfaces.screenshot_service import IScreenshotService
from src.domain.interfaces.monitoring_service import IMonitoringService
from src.utils.platform_detection import is_wsl, is_windows, is_linux_with_display


class ScreenAgentApp:
    """Main application class for ScreenAgent"""
    
    def __init__(self):
        print("🔧 Initializing ScreenAgent...")
        
        # Initialize DI container with configuration
        print("🏗️  Setting up dependency injection container...")
        try:
            # Detect platform
            if is_wsl():
                platform_name = "wsl"
            elif is_windows():
                platform_name = "windows"
            elif is_linux_with_display():
                platform_name = "linux"
            else:
                platform_name = "unknown"
            
            # Basic configuration dictionary for DI container
            config_dict = {
                "storage": {
                    "type": "file",
                    "base_path": "screenshots"
                },
                "monitoring": {
                    "default_strategy": "threshold",
                    "threshold": 20
                },
                "capture": {
                    "platform": platform_name,
                    "wsl_enabled": is_wsl()
                },
                "server": {
                    "port": 8000,
                    "max_port_attempts": 10
                },
                "config_file": "config/screen_agent_config.json"
            }
            
            setup_container(config_dict)
            print("✅ Dependency injection container initialized")
            
            # Get clean architecture services from container
            container = get_container()
            self.screenshot_service = container.get(IScreenshotService)
            self.monitoring_service = container.get(IMonitoringService) 
            
            # Create Flask app (replaces old custom server)
            from src.api.flask_app import create_app
            self.app = create_app()
            self.server = None  # Flask handles server internally
            
        except Exception as e:
            print(f"❌ Failed to initialize clean architecture: {e}")
            print("    Application cannot start without proper dependency injection")
            raise
        
        self._running = False
        self._server_thread = None
    
    def start(self):
        """Start the ScreenAgent application"""
        print("🚀 Starting ScreenAgent...")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Services are already initialized via DI container
            print("✅ Services initialized via dependency injection")
            
            # Start the web server
            if not self._start_server():
                print("❌ Failed to start web server")
                return False
            
            # ROI monitoring is now handled by the clean architecture services
            print("✅ ROI monitoring available through clean architecture services")
            
            # TODO: Start keyboard handler once it's integrated with clean architecture
            # self._start_keyboard_handler()
            
            self._running = True
            print(f"✅ ScreenAgent is running at http://localhost:{self.port}")
            print(f"📚 Swagger documentation available at: http://localhost:{self.port}/docs/")
            print("Press Ctrl+C to stop")
            
            # Take initial screenshot
            self._take_initial_screenshot()
            
            # Keep the main thread alive
            self._wait_for_shutdown()
            
        except Exception as e:
            print(f"❌ Error starting ScreenAgent: {e}")
            return False
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Stop the ScreenAgent application"""
        if not self._running:
            return
        
        print("\n🛑 Stopping ScreenAgent...")
        self._running = False
        
        # Flask server stops automatically when threads finish
        # No explicit stop method needed
        
        # Wait for threads to finish
        self._join_threads()
        
        print("✅ ScreenAgent stopped successfully")
    
    def _start_server(self) -> bool:
        """Start the Flask web server in a separate thread"""
        try:
            import os
            import threading
            
            # Get configuration from environment or use defaults
            host = os.environ.get('FLASK_HOST', '0.0.0.0')
            port = int(os.environ.get('FLASK_PORT', 8000))
            
            # Store port for access by other methods
            self.port = port
            
            def run_flask_app():
                self.app.run(
                    host=host,
                    port=port,
                    debug=False,  # No debug in production
                    use_reloader=False  # No reloader in production
                )
            
            self._server_thread = threading.Thread(
                target=run_flask_app,
                daemon=True
            )
            self._server_thread.start()
            return True
        except Exception as e:
            print(f"Error starting Flask server: {e}")
            return False
    
    def _start_keyboard_handler(self):
        """Start keyboard handler if available (disabled for clean architecture)"""
        # TODO: Reimplement keyboard handler with clean architecture
        pass
    
    def _take_initial_screenshot(self):
        """Take an initial screenshot using clean architecture"""
        try:
            import asyncio
            
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Get configuration from DI container
            container = get_container()
            from src.domain.repositories.configuration_repository import IConfigurationRepository
            config_repo = container.get(IConfigurationRepository)
            
            # Get ROI from configuration
            roi = loop.run_until_complete(config_repo.get_config("roi"))
            
            # Use clean architecture screenshot service
            if roi:
                from src.domain.value_objects.coordinates import Rectangle
                region = Rectangle(left=roi[0], top=roi[1], right=roi[2], bottom=roi[3])
                screenshot = loop.run_until_complete(
                    self.screenshot_service.capture_region(region)
                )
            else:
                screenshot = loop.run_until_complete(
                    self.screenshot_service.capture_full_screen()
                )
            
            if screenshot:
                print(f"📸 Initial screenshot taken: {screenshot.id}")
        except Exception as e:
            print(f"⚠️  Failed to take initial screenshot: {e}")
    
    def _wait_for_shutdown(self):
        """Wait for shutdown signal"""
        try:
            while self._running:
                threading.Event().wait(1)
        except KeyboardInterrupt:
            pass
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n📡 Received signal {signum}")
        self._running = False
    
    def _join_threads(self):
        """Wait for server thread to finish"""
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=5)


def main():
    """Main entry point"""
    print("🎯 ScreenAgent - Smart Screen Monitoring")
    print("=" * 40)
    
    app = ScreenAgentApp()
    success = app.start()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
