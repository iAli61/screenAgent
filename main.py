"""
ScreenAgent Core Application
Refactored for better organization and maintainability
"""
import os
import sys
import asyncio
import threading
import socketserver
from datetime import datetime
from typing import Optional, List, Tuple
import signal

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.core.config import Config
from src.core.screenshot_manager import ScreenshotManager
from src.core.roi_monitor import ROIMonitor
from src.api.server import ScreenAgentServer
from src.core.keyboard_handler import KeyboardHandler


class ScreenAgentApp:
    """Main application class for ScreenAgent"""
    
    def __init__(self):
        self.config = Config()
        self.screenshot_manager = ScreenshotManager(self.config)
        self.roi_monitor = ROIMonitor(self.config)
        self.server = ScreenAgentServer(self.screenshot_manager, self.roi_monitor, self.config)
        self.keyboard_handler = KeyboardHandler(self.screenshot_manager)
        
        self._running = False
        self._server_thread = None
        self._monitor_thread = None
        self._keyboard_thread = None
    
    def start(self):
        """Start the ScreenAgent application"""
        print("🚀 Starting ScreenAgent...")
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            # Initialize screenshot manager
            if not self.screenshot_manager.initialize():
                print("❌ Failed to initialize screenshot functionality")
                return False
            
            # Start the web server
            if not self._start_server():
                print("❌ Failed to start web server")
                return False
            
            # Start ROI monitoring
            self._start_roi_monitor()
            
            # Start keyboard handler if available
            self._start_keyboard_handler()
            
            self._running = True
            print(f"✅ ScreenAgent is running at http://localhost:{self.server.port}")
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
        
        # Stop all components
        if self.roi_monitor:
            self.roi_monitor.stop()
        
        if self.keyboard_handler:
            self.keyboard_handler.stop()
        
        if self.server:
            self.server.stop()
        
        # Wait for threads to finish
        self._join_threads()
        
        print("✅ ScreenAgent stopped successfully")
    
    def _start_server(self) -> bool:
        """Start the web server in a separate thread"""
        try:
            port = self.server.find_available_port()
            if port is None:
                return False
            
            self._server_thread = threading.Thread(
                target=self.server.start,
                args=(port,),
                daemon=True
            )
            self._server_thread.start()
            return True
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    def _start_roi_monitor(self):
        """Start ROI monitoring in a separate thread"""
        self._monitor_thread = threading.Thread(
            target=self.roi_monitor.start,
            daemon=True
        )
        self._monitor_thread.start()
    
    def _start_keyboard_handler(self):
        """Start keyboard handler if available"""
        if self.keyboard_handler.is_available():
            self._keyboard_thread = threading.Thread(
                target=self.keyboard_handler.start,
                daemon=True
            )
            self._keyboard_thread.start()
        else:
            print("⚠️  Keyboard shortcuts not available (requires root permissions on Linux)")
    
    def _take_initial_screenshot(self):
        """Take an initial screenshot"""
        try:
            roi = self.config.get('roi')
            if roi:
                screenshot = self.screenshot_manager.take_screenshot(roi)
                if screenshot:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.screenshot_manager.add_screenshot(timestamp, screenshot)
                    print(f"📸 Initial screenshot taken at {timestamp}")
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
        """Wait for all threads to finish"""
        threads = [
            self._server_thread,
            self._monitor_thread,
            self._keyboard_thread
        ]
        
        for thread in threads:
            if thread and thread.is_alive():
                thread.join(timeout=5)


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
