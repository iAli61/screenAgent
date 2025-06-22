#!/usr/bin/env python3
"""
Debug test for LLM response management
"""

import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_mock_config():
    """Create a mock config object for testing"""
    config = Mock()
    config.get = Mock(side_effect=lambda key, default=None: {
        'max_screenshots': 5,
        'auto_cleanup': True,
        'change_threshold': 10.0,
        'check_interval': 1.0,
        'llm_enabled': True
    }.get(key, default))
    
    # Create temp directory for testing
    temp_dir = tempfile.mkdtemp()
    config.temp_screenshot_path = os.path.join(temp_dir, 'temp_screenshot.png')
    config.roi = (100, 100, 200, 200)
    config.change_threshold = 10.0
    config.check_interval = 1.0
    config.llm_enabled = True
    
    return config, temp_dir

def create_mock_screenshot_data(width=100, height=100):
    """Create mock screenshot data as bytes"""
    # Create a simple PNG-like data structure
    data_size = width * height // 100
    return b'\x89PNG\r\n\x1a\n' + b'mock_image_data' * data_size

def debug_llm_test():
    print("🔧 Debug LLM Response Test...")
    
    config, temp_dir = create_mock_config()
    
    try:
        with patch('src.core.storage.screenshot_manager.ScreenshotCapture'), \
             patch('src.core.storage.screenshot_manager.ROIMonitor'), \
             patch('src.core.storage.screenshot_manager.KeyboardHandler'):
            
            from src.core.storage.screenshot_manager import ScreenshotManager
            manager = ScreenshotManager(config)
            
            # Add screenshots
            for i in range(3):
                screenshot_data = create_mock_screenshot_data()
                timestamp = f"2025-06-21_{i:02d}:00:00"
                manager.add_screenshot(timestamp, screenshot_data)
                print(f"Added screenshot {i} with timestamp {timestamp}")
            
            print(f"Total screenshots: {manager.get_screenshot_count()}")
            print(f"LLM responses before: {manager._llm_responses}")
            
            # Set LLM responses
            manager.set_llm_response(0, "First response")
            manager.set_llm_response(2, "Third response")
            
            print(f"LLM responses after: {manager._llm_responses}")
            
            # Check individual responses
            print(f"Response 0: {manager.get_llm_response(0)}")
            print(f"Response 1: {manager.get_llm_response(1)}")
            print(f"Response 2: {manager.get_llm_response(2)}")
            
            # Check all screenshots
            all_screenshots = manager.get_all_screenshots()
            print(f"All screenshots count: {len(all_screenshots)}")
            
            for i, screenshot in enumerate(all_screenshots):
                print(f"Screenshot {i}: timestamp={screenshot['timestamp']}, llm_response={screenshot['llm_response']}")
                
            # The issue might be here - memory limits causing cleanup
            if len(all_screenshots) != 3:
                print(f"WARNING: Expected 3 screenshots but got {len(all_screenshots)}")
                print("This might be due to memory cleanup during add_screenshot")
                
            manager.cleanup()
            
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    debug_llm_test()
