#!/usr/bin/env python3
"""
Screenshot Server - A server for taking and monitoring screenshots of a region of interest.
"""
import socket
import threading
import socketserver
import numpy as np
import time
from datetime import datetime
import sys

# Import our modular components
from config import load_from_config, DEFAULT_PORT, DEFAULT_ROI, MAX_PORT_ATTEMPTS, CHANGE_THRESHOLD, CHECK_INTERVAL
from platform_detection import WSL_MODE
from screenshot import take_screenshot
from keyboard_handler import setup_keyboard, start_keyboard_listener
from server_handler import ScreenshotHandler

def find_available_port(start_port, max_attempts):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            if result != 0:  # Port is available
                return port
    raise OSError(f"Could not find an available port in range {start_port}-{start_port + max_attempts - 1}")

def has_roi_changed(last_screenshot, new_screenshot):
    """Check if the ROI has changed significantly"""
    if last_screenshot is None:
        return False
    
    try:
        # Convert bytes to images for comparison
        from PIL import Image
        import io
        img1 = Image.open(io.BytesIO(last_screenshot))
        img2 = Image.open(io.BytesIO(new_screenshot))
        
        # Convert to numpy arrays for comparison
        np1 = np.array(img1)
        np2 = np.array(img2)
        
        # Calculate mean absolute difference
        diff = np.mean(np.abs(np1 - np2))
        
        return diff > CHANGE_THRESHOLD
    except Exception as e:
        print(f"Error comparing screenshots: {e}")
        return False

def monitor_roi(roi):
    """Wait for manual triggers to take screenshots"""
    
    print(f"Screenshot service ready. Visit http://localhost:{PORT}/trigger for manual screenshot.")
    
    # Initial screenshot
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    initial_screenshot = take_screenshot(roi)
    ScreenshotHandler.add_screenshot(timestamp, initial_screenshot)
    print(f"Initial screenshot taken at {timestamp}")
    
    # Wait indefinitely - screenshots will only be taken when manually triggered
    while True:
        time.sleep(60)  # Just keep the thread alive with minimal processing

def take_manual_screenshot():
    """Callback for keyboard shortcuts to take a manual screenshot"""
    roi = ScreenshotHandler.roi
    screenshot = take_screenshot(roi)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ScreenshotHandler.add_screenshot(timestamp, screenshot)
    print(f"Manual screenshot taken at {timestamp}")
    return screenshot

def main():
    global PORT
    
    # Load configuration
    roi = load_from_config('roi', DEFAULT_ROI)
    ScreenshotHandler.set_roi(roi)
    
    # Setup keyboard if available
    keyboard_available = setup_keyboard()
    
    # Find an available port
    try:
        PORT = find_available_port(DEFAULT_PORT, MAX_PORT_ATTEMPTS)
        print(f"Using port {PORT}")
    except OSError as e:
        print(f"Error: {e}")
        return
    
    # Start the server
    handler = ScreenshotHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"Server started at http://localhost:{PORT}")
    
    # Start keyboard listener if available
    if keyboard_available:
        keyboard_thread = start_keyboard_listener(take_manual_screenshot)
        if keyboard_thread:
            keyboard_thread.start()
    
    # Start ROI monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_roi, args=(roi,), daemon=True)
    monitor_thread.start()
    
    # Run the server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
        httpd.server_close()

if __name__ == "__main__":
    PORT = DEFAULT_PORT
    main()