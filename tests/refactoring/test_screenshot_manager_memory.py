#!/usr/bin/env python3
"""
Comprehensive test suite for ScreenshotManager memory management
Tests memory initialization, cleanup, and functionality
"""

import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import io

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

class TestScreenshotManagerMemory:
    """Test class for ScreenshotManager memory management"""
    
    def __init__(self):
        self.config = None
        self.temp_dir = None
        self.manager = None
        
    def setup(self):
        """Set up test environment"""
        print("🔧 Setting up test environment...")
        self.config, self.temp_dir = create_mock_config()
        
        # Mock the dependencies
        with patch('src.core.storage.screenshot_manager.ScreenshotCapture'), \
             patch('src.core.storage.screenshot_manager.ROIMonitor'), \
             patch('src.core.storage.screenshot_manager.KeyboardHandler'):
            
            from src.core.storage.screenshot_manager import ScreenshotManager
            self.manager = ScreenshotManager(self.config)
        
        print("✅ Test environment setup complete")
        
    def teardown(self):
        """Clean up test environment"""
        print("🧹 Cleaning up test environment...")
        if self.manager:
            self.manager.cleanup()
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        print("✅ Test environment cleaned up")
    
    def test_memory_initialization(self):
        """Test that memory is properly initialized on instantiation"""
        print("\n📋 Testing memory initialization...")
        
        # Check initial state
        assert hasattr(self.manager, '_screenshots'), "Screenshots list not initialized"
        assert hasattr(self.manager, '_llm_responses'), "LLM responses dict not initialized"
        assert len(self.manager._screenshots) == 0, "Screenshots list should be empty on init"
        assert len(self.manager._llm_responses) == 0, "LLM responses should be empty on init"
        
        # Check memory usage
        memory_usage = self.manager.get_memory_usage()
        assert memory_usage['screenshot_count'] == 0, "Screenshot count should be 0"
        assert memory_usage['total_size_bytes'] == 0, "Total size should be 0"
        assert memory_usage['llm_responses_count'] == 0, "LLM responses count should be 0"
        
        print("✅ Memory initialization test passed")
    
    def test_add_screenshots(self):
        """Test adding screenshots to memory"""
        print("\n📋 Testing screenshot addition...")
        
        # Add some screenshots
        for i in range(3):
            screenshot_data = create_mock_screenshot_data()
            timestamp = f"2025-06-21_{i:02d}:00:00"
            metadata = {'test': f'screenshot_{i}'}
            
            self.manager.add_screenshot(timestamp, screenshot_data, metadata)
        
        # Check state
        assert self.manager.get_screenshot_count() == 3, "Should have 3 screenshots"
        
        # Check memory usage
        memory_usage = self.manager.get_memory_usage()
        assert memory_usage['screenshot_count'] == 3, "Memory usage should show 3 screenshots"
        assert memory_usage['total_size_bytes'] > 0, "Total size should be > 0"
        
        # Check individual screenshots
        for i in range(3):
            screenshot = self.manager.get_screenshot(i)
            assert screenshot is not None, f"Screenshot {i} should exist"
            assert screenshot['metadata']['test'] == f'screenshot_{i}', "Metadata should match"
        
        print("✅ Screenshot addition test passed")
    
    def test_memory_limits(self):
        """Test memory cleanup when exceeding limits"""
        print("\n📋 Testing memory limits...")
        
        # Add more screenshots than the limit (5)
        for i in range(8):
            screenshot_data = create_mock_screenshot_data()
            timestamp = f"2025-06-21_{i:02d}:00:00"
            self.manager.add_screenshot(timestamp, screenshot_data)
        
        # Should be limited to max_screenshots (5)
        assert self.manager.get_screenshot_count() == 5, "Should be limited to max_screenshots"
        
        # Check that newest screenshots are kept
        latest = self.manager.get_latest_screenshot()
        assert latest is not None, "Should have latest screenshot"
        assert "07:00:00" in latest['timestamp'], "Latest should be the most recent"
        
        print("✅ Memory limits test passed")
    
    def test_clear_all_screenshots(self):
        """Test clearing all screenshots"""
        print("\n📋 Testing clear all screenshots...")
        
        # Add some screenshots
        for i in range(3):
            screenshot_data = create_mock_screenshot_data()
            timestamp = f"2025-06-21_{i:02d}:00:00"
            self.manager.add_screenshot(timestamp, screenshot_data)
        
        # Add some LLM responses
        self.manager.set_llm_response(0, "Response 1")
        self.manager.set_llm_response(1, "Response 2")
        
        # Clear all
        result = self.manager.clear_all_screenshots()
        assert result == True, "Clear should return True"
        
        # Check everything is cleared
        assert self.manager.get_screenshot_count() == 0, "Screenshot count should be 0"
        assert len(self.manager._llm_responses) == 0, "LLM responses should be cleared"
        
        # Check memory usage
        memory_usage = self.manager.get_memory_usage()
        assert memory_usage['screenshot_count'] == 0, "Memory usage should show 0 screenshots"
        assert memory_usage['total_size_bytes'] == 0, "Total size should be 0"
        
        print("✅ Clear all screenshots test passed")
    
    def test_reset_memory(self):
        """Test memory reset functionality"""
        print("\n📋 Testing memory reset...")
        
        # Add some data
        for i in range(2):
            screenshot_data = create_mock_screenshot_data()
            timestamp = f"2025-06-21_{i:02d}:00:00"
            self.manager.add_screenshot(timestamp, screenshot_data)
        
        self.manager.set_llm_response(0, "Test response")
        
        # Reset memory
        result = self.manager.reset_memory()
        assert result == True, "Reset should return True"
        
        # Check everything is reset
        assert self.manager.get_screenshot_count() == 0, "Screenshot count should be 0"
        assert len(self.manager._llm_responses) == 0, "LLM responses should be cleared"
        assert hasattr(self.manager, '_screenshots'), "Screenshots list should still exist"
        assert hasattr(self.manager, '_llm_responses'), "LLM responses dict should still exist"
        
        print("✅ Memory reset test passed")
    
    def test_delete_screenshot(self):
        """Test deleting individual screenshots"""
        print("\n📋 Testing screenshot deletion...")
        
        # Add screenshots with LLM responses
        for i in range(3):
            screenshot_data = create_mock_screenshot_data()
            timestamp = f"2025-06-21_{i:02d}:00:00"
            self.manager.add_screenshot(timestamp, screenshot_data)
            self.manager.set_llm_response(i, f"Response {i}")
        
        # Delete middle screenshot
        result = self.manager.delete_screenshot(1)
        assert result == True, "Delete should return True"
        
        # Check count
        assert self.manager.get_screenshot_count() == 2, "Should have 2 screenshots left"
        
        # Check LLM responses were adjusted
        assert self.manager.get_llm_response(0) == "Response 0", "First response should remain"
        assert self.manager.get_llm_response(1) == "Response 2", "Third response should move to index 1"
        assert self.manager.get_llm_response(2) is None, "Index 2 should be empty"
        
        print("✅ Screenshot deletion test passed")
    
    def test_llm_responses(self):
        """Test LLM response management"""
        print("\n📋 Testing LLM response management...")
        
        # Add screenshots
        for i in range(3):
            screenshot_data = create_mock_screenshot_data()
            timestamp = f"2025-06-21_{i:02d}:00:00"
            self.manager.add_screenshot(timestamp, screenshot_data)
        
        # Set LLM responses
        self.manager.set_llm_response(0, "First response")
        self.manager.set_llm_response(2, "Third response")
        
        # Check responses
        assert self.manager.get_llm_response(0) == "First response", "First response should match"
        assert self.manager.get_llm_response(1) is None, "Second response should be None"
        assert self.manager.get_llm_response(2) == "Third response", "Third response should match"
        
        # Check all screenshots include LLM responses
        all_screenshots = self.manager.get_all_screenshots()
        assert len(all_screenshots) == 3, "Should have 3 screenshots"
        
        # Debug print
        print(f"Debug: all_screenshots = {all_screenshots}")
        print(f"Debug: LLM responses dict = {self.manager._llm_responses}")
        
        assert all_screenshots[0]['llm_response'] == "First response", f"First should have response, got: {all_screenshots[0]['llm_response']}"
        assert all_screenshots[1]['llm_response'] is None, f"Second should have None, got: {all_screenshots[1]['llm_response']}"
        assert all_screenshots[2]['llm_response'] == "Third response", f"Third should have response, got: {all_screenshots[2]['llm_response']}"
        
        print("✅ LLM response management test passed")
    
    def test_cleanup_functionality(self):
        """Test cleanup functionality"""
        print("\n📋 Testing cleanup functionality...")
        
        # Add some data
        for i in range(2):
            screenshot_data = create_mock_screenshot_data()
            timestamp = f"2025-06-21_{i:02d}:00:00"
            self.manager.add_screenshot(timestamp, screenshot_data)
        
        self.manager.set_llm_response(0, "Test response")
        
        # Set monitoring to true (mock)
        self.manager._monitoring = True
        
        # Cleanup
        self.manager.cleanup()
        
        # Check everything is cleaned
        assert self.manager.get_screenshot_count() == 0, "Screenshots should be cleared"
        assert len(self.manager._llm_responses) == 0, "LLM responses should be cleared"
        assert self.manager._monitoring == False, "Monitoring should be stopped"
        
        print("✅ Cleanup functionality test passed")
    
    def test_memory_usage_reporting(self):
        """Test memory usage reporting"""
        print("\n📋 Testing memory usage reporting...")
        
        # Add screenshots of different sizes
        small_data = create_mock_screenshot_data(50, 50)
        large_data = create_mock_screenshot_data(200, 200)
        
        self.manager.add_screenshot("2025-06-21_01:00:00", small_data)
        self.manager.add_screenshot("2025-06-21_02:00:00", large_data)
        self.manager.set_llm_response(0, "Response")
        
        # Check memory usage
        usage = self.manager.get_memory_usage()
        
        assert usage['screenshot_count'] == 2, "Should show 2 screenshots"
        assert usage['total_size_bytes'] > 0, "Should show total size"
        assert usage['total_size_mb'] > 0, "Should show MB size"
        assert usage['max_screenshots'] == 5, "Should show max limit"
        assert usage['llm_responses_count'] == 1, "Should show 1 LLM response"
        assert 0 <= usage['memory_usage_percentage'] <= 100, "Percentage should be valid"
        
        print("✅ Memory usage reporting test passed")
    
    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting ScreenshotManager memory management tests...")
        
        try:
            self.setup()
            
            # Run all test methods
            self.test_memory_initialization()
            self.test_add_screenshots()
            self.test_memory_limits()
            self.test_clear_all_screenshots()
            self.test_reset_memory()
            self.test_delete_screenshot()
            self.test_llm_responses()
            self.test_cleanup_functionality()
            self.test_memory_usage_reporting()
            
            print("\n🎉 All tests passed successfully!")
            return True
            
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
            return False
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.teardown()

def test_initialization_scenarios():
    """Test different initialization scenarios"""
    print("\n🔧 Testing initialization scenarios...")
    
    # Test 1: Normal initialization
    config, temp_dir = create_mock_config()
    try:
        with patch('src.core.storage.screenshot_manager.ScreenshotCapture'), \
             patch('src.core.storage.screenshot_manager.ROIMonitor'), \
             patch('src.core.storage.screenshot_manager.KeyboardHandler'):
            
            from src.core.storage.screenshot_manager import ScreenshotManager
            manager = ScreenshotManager(config)
            
            assert manager.get_screenshot_count() == 0, "New instance should have empty memory"
            print("✅ Normal initialization test passed")
            
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    # Test 2: Initialization with existing temp file
    config, temp_dir = create_mock_config()
    try:
        # Create a temp file first
        os.makedirs(os.path.dirname(config.temp_screenshot_path), exist_ok=True)
        with open(config.temp_screenshot_path, 'wb') as f:
            f.write(b'existing_temp_data')
        
        with patch('src.core.storage.screenshot_manager.ScreenshotCapture'), \
             patch('src.core.storage.screenshot_manager.ROIMonitor'), \
             patch('src.core.storage.screenshot_manager.KeyboardHandler'):
            
            manager = ScreenshotManager(config)
            
            # Temp file should be cleaned up
            assert not os.path.exists(config.temp_screenshot_path), "Temp file should be cleaned up"
            print("✅ Temp file cleanup test passed")
            
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def test_error_handling():
    """Test error handling in memory operations"""
    print("\n🔧 Testing error handling...")
    
    config, temp_dir = create_mock_config()
    try:
        with patch('src.core.storage.screenshot_manager.ScreenshotCapture'), \
             patch('src.core.storage.screenshot_manager.ROIMonitor'), \
             patch('src.core.storage.screenshot_manager.KeyboardHandler'):
            
            from src.core.storage.screenshot_manager import ScreenshotManager
            manager = ScreenshotManager(config)
            
            # Test accessing non-existent screenshot
            assert manager.get_screenshot(999) is None, "Non-existent screenshot should return None"
            assert manager.get_screenshot_data(999) is None, "Non-existent data should return None"
            assert manager.get_llm_response(999) is None, "Non-existent response should return None"
            
            # Test deleting non-existent screenshot
            assert manager.delete_screenshot(999) == False, "Deleting non-existent should return False"
            
            # Test setting LLM response for non-existent screenshot
            manager.set_llm_response(999, "test")  # Should not crash
            assert manager.get_llm_response(999) is None, "Invalid index should not store response"
            
            print("✅ Error handling test passed")
            
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    # Run the comprehensive test suite
    tester = TestScreenshotManagerMemory()
    success = tester.run_all_tests()
    
    # Run additional scenario tests
    test_initialization_scenarios()
    test_error_handling()
    
    if success:
        print("\n🎊 All ScreenshotManager memory management tests completed successfully!")
        print("✅ Memory initialization is working correctly")
        print("✅ Memory cleanup is working correctly") 
        print("✅ Memory limits are enforced properly")
        print("✅ Error handling is robust")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
