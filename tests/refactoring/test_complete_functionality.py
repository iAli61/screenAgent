#!/usr/bin/env python3
"""
Integration test for the actual ScreenshotManager class with real dependencies
"""

import sys
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_real_screenshot_manager():
    """Test the actual ScreenshotManager with mocked dependencies"""
    print("🚀 Testing Real ScreenshotManager Memory Management...")
    
    # Create a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create a mock config
        config = Mock()
        config.get = Mock(side_effect=lambda key, default=None: {
            'max_screenshots': 3,
            'auto_cleanup': True,
            'change_threshold': 10.0,
            'check_interval': 1.0,
            'llm_enabled': True
        }.get(key, default))
        
        config.temp_screenshot_path = os.path.join(temp_dir, 'temp_screenshot.png')
        config.roi = (100, 100, 200, 200)
        config.change_threshold = 10.0
        config.check_interval = 1.0
        config.llm_enabled = True
        
        # Mock the dependencies that require real system components
        with patch('src.core.storage.screenshot_manager.ScreenshotCapture') as MockScreenshotCapture, \
             patch('src.core.storage.screenshot_manager.ROIMonitor') as MockROIMonitor, \
             patch('src.core.storage.screenshot_manager.KeyboardHandler') as MockKeyboardHandler:
            
            # Configure mocks
            mock_capture = Mock()
            mock_capture.initialize.return_value = True
            mock_capture.method = "mocked"
            MockScreenshotCapture.return_value = mock_capture
            
            mock_roi = Mock()
            mock_roi.initialize.return_value = True
            mock_roi.get_history.return_value = []
            MockROIMonitor.return_value = mock_roi
            
            mock_keyboard = Mock()
            mock_keyboard.initialize.return_value = True
            MockKeyboardHandler.return_value = mock_keyboard
            
            # Import and create ScreenshotManager
            from src.core.storage.screenshot_manager import ScreenshotManager
            manager = ScreenshotManager(config)
            
            print("✅ ScreenshotManager created successfully")
            
            # Test 1: Initial memory state
            print("\n📋 Test 1: Initial Memory State")
            assert manager.get_screenshot_count() == 0, "Should start with 0 screenshots"
            memory_usage = manager.get_memory_usage()
            assert memory_usage['screenshot_count'] == 0, "Memory usage should show 0"
            print("✅ Initial memory state test passed")
            
            # Test 2: Initialize components
            print("\n📋 Test 2: Component Initialization")
            result = manager.initialize()
            assert result == True, "Initialize should return True"
            assert manager.get_screenshot_count() == 0, "Memory should still be clean after init"
            print("✅ Component initialization test passed")
            
            # Test 3: Add screenshots
            print("\n📋 Test 3: Adding Screenshots")
            test_data = b'test_screenshot_data_' * 100
            for i in range(5):  # Add more than the limit (3)
                manager.add_screenshot(f"2025-06-21_{i:02d}:00:00", test_data, {'test': i})
            
            # Should be limited to max_screenshots
            assert manager.get_screenshot_count() == 3, f"Should be limited to 3, got {manager.get_screenshot_count()}"
            print("✅ Screenshot addition with limits test passed")
            
            # Test 4: LLM responses
            print("\n📋 Test 4: LLM Response Management")
            manager.set_llm_response(0, "First response")
            manager.set_llm_response(2, "Third response")
            
            all_screenshots = manager.get_all_screenshots()
            assert len(all_screenshots) == 3, "Should have 3 screenshots"
            assert all_screenshots[0]['llm_response'] == "First response", "First should have response"
            assert all_screenshots[1]['llm_response'] is None, "Second should be None"
            assert all_screenshots[2]['llm_response'] == "Third response", "Third should have response"
            print("✅ LLM response management test passed")
            
            # Test 5: Memory usage reporting
            print("\n📋 Test 5: Memory Usage Reporting")
            usage = manager.get_memory_usage()
            assert usage['screenshot_count'] == 3, "Should show 3 screenshots"
            assert usage['total_size_bytes'] > 0, "Should show total size > 0"
            assert usage['max_screenshots'] == 3, "Should show correct max"
            assert usage['llm_responses_count'] == 2, "Should show 2 LLM responses"
            print("✅ Memory usage reporting test passed")
            
            # Test 6: Status reporting
            print("\n📋 Test 6: Status Reporting")
            status = manager.get_status()
            assert status['screenshot_count'] == 3, "Status should show correct count"
            assert status['monitoring'] == False, "Should not be monitoring initially"
            assert 'roi' in status, "Should include ROI info"
            assert 'settings' in status, "Should include settings"
            print("✅ Status reporting test passed")
            
            # Test 7: Clear all functionality
            print("\n📋 Test 7: Clear All Functionality")
            result = manager.clear_all_screenshots()
            assert result == True, "Clear should return True"
            assert manager.get_screenshot_count() == 0, "Should have 0 after clear"
            assert len(manager._llm_responses) == 0, "LLM responses should be cleared"
            print("✅ Clear all functionality test passed")
            
            # Test 8: Cleanup
            print("\n📋 Test 8: Cleanup")
            # Add some data first
            manager.add_screenshot("test", test_data)
            manager.set_llm_response(0, "test response")
            
            # Cleanup
            manager.cleanup()
            assert manager.get_screenshot_count() == 0, "Cleanup should clear screenshots"
            assert len(manager._llm_responses) == 0, "Cleanup should clear LLM responses"
            print("✅ Cleanup test passed")
            
            print("\n🎉 All real ScreenshotManager tests passed!")
            return True
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def test_memory_persistence():
    """Test that memory cleanup works properly between instances"""
    print("\n🔄 Testing Memory Persistence Between Instances...")
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create config
        config = Mock()
        config.get = Mock(side_effect=lambda key, default=None: {
            'max_screenshots': 5,
            'auto_cleanup': True
        }.get(key, default))
        config.temp_screenshot_path = os.path.join(temp_dir, 'temp.png')
        
        with patch('src.core.storage.screenshot_manager.ScreenshotCapture'), \
             patch('src.core.storage.screenshot_manager.ROIMonitor'), \
             patch('src.core.storage.screenshot_manager.KeyboardHandler'):
            
            from src.core.storage.screenshot_manager import ScreenshotManager
            
            # Create first instance and add data
            manager1 = ScreenshotManager(config)
            manager1.add_screenshot("test1", b'data1')
            manager1.set_llm_response(0, "response1")
            assert manager1.get_screenshot_count() == 1, "First instance should have 1 screenshot"
            
            # Create second instance - should have clean memory
            manager2 = ScreenshotManager(config)
            assert manager2.get_screenshot_count() == 0, "Second instance should start clean"
            assert len(manager2._llm_responses) == 0, "Second instance should have no LLM responses"
            
            # Add data to second instance
            manager2.add_screenshot("test2", b'data2')
            assert manager2.get_screenshot_count() == 1, "Second instance should have its own data"
            
            # First instance should still have its data (different objects)
            assert manager1.get_screenshot_count() == 1, "First instance should retain its data"
            
            print("✅ Memory persistence test passed - each instance has clean, separate memory")
            return True
            
    except Exception as e:
        print(f"❌ Memory persistence test failed: {e}")
        return False
        
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    print("🧪 Running Comprehensive ScreenshotManager Tests...\n")
    
    test1_success = test_real_screenshot_manager()
    test2_success = test_memory_persistence()
    
    if test1_success and test2_success:
        print("\n🎊 ALL TESTS PASSED! 🎊")
        print("\n✅ ScreenshotManager refactoring is complete and working correctly!")
        print("✅ Memory is properly cleaned on instantiation")
        print("✅ Memory limits are enforced")
        print("✅ LLM response management works correctly")
        print("✅ Each instance has clean, separate memory")
        print("✅ All memory management methods work as expected")
        print("✅ Cleanup and resource management work properly")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
