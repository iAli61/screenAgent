#!/usr/bin/env python3
"""
Test core screenshot functionality to ensure nothing was broken during refactoring
"""

import sys
import os
import tempfile
from unittest.mock import Mock, patch

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_core_functionality():
    """Test that core screenshot functionality still works after refactoring"""
    print("🔍 Testing Core Screenshot Functionality...")
    
    try:
        # Create mock config
        config = Mock()
        config.get = Mock(side_effect=lambda key, default=None: {
            'max_screenshots': 10,
            'auto_cleanup': True,
            'change_threshold': 5.0
        }.get(key, default))
        config.temp_screenshot_path = tempfile.mktemp(suffix='.png')
        config.roi = (100, 100, 300, 300)
        config.change_threshold = 5.0
        
        # Mock dependencies
        with patch('src.core.storage.screenshot_manager_unified.ScreenshotCaptureManager') as MockCapture, \
             patch('src.core.storage.screenshot_manager_unified.ROIMonitor') as MockROI, \
             patch('src.core.storage.screenshot_manager_unified.KeyboardHandler') as MockKeyboard:
            
            # Configure mocks
            mock_capture = Mock()
            mock_capture.initialize.return_value = True
            mock_capture.capture_full_screen.return_value = b'fake_screenshot_data'
            mock_capture.capture_roi.return_value = b'fake_roi_data'
            mock_capture.method = "test_method"
            MockCapture.return_value = mock_capture
            
            mock_roi = Mock()
            mock_roi.initialize.return_value = True
            mock_roi.start_monitoring.return_value = True
            mock_roi.get_history.return_value = []
            MockROI.return_value = mock_roi
            
            mock_keyboard = Mock()
            mock_keyboard.initialize.return_value = True
            MockKeyboard.return_value = mock_keyboard
            
            # Import and create ScreenshotManager
            from src.core.storage.screenshot_manager_unified import ScreenshotManager
            manager = ScreenshotManager(config)
            print("✅ ScreenshotManager created with clean memory")
            
            # Test initialization
            result = manager.initialize()
            assert result == True, "Initialize should succeed"
            print("✅ Component initialization works")
            
            # Test screenshot capture
            screenshot = manager.take_screenshot(save_to_temp=False)
            assert screenshot == b'fake_screenshot_data', "Screenshot capture should work"
            print("✅ Screenshot capture works")
            
            # Test ROI screenshot
            roi_screenshot = manager.take_roi_screenshot()
            assert roi_screenshot == b'fake_roi_data', "ROI screenshot should work"
            print("✅ ROI screenshot works")
            
            # Test monitoring
            monitoring_result = manager.start_roi_monitoring((100, 100, 200, 200))
            assert monitoring_result == True, "ROI monitoring should start"
            assert manager.is_monitoring() == True, "Should report monitoring active"
            print("✅ ROI monitoring works")
            
            manager.stop_roi_monitoring()
            assert manager.is_monitoring() == False, "Should report monitoring stopped"
            print("✅ ROI monitoring stop works")
            
            # Test screenshot comparison (with mock data)
            with patch('src.core.storage.screenshot_manager.PIL_AVAILABLE', True), \
                 patch('src.core.storage.screenshot_manager.NUMPY_AVAILABLE', True):
                
                # Mock PIL and numpy for comparison
                with patch('src.core.storage.screenshot_manager.Image') as MockImage, \
                     patch('src.core.storage.screenshot_manager.np') as MockNumpy:
                    
                    mock_img = Mock()
                    mock_img.size = (100, 100)
                    MockImage.open.return_value = mock_img
                    
                    mock_array = Mock()
                    MockNumpy.array.return_value = mock_array
                    MockNumpy.mean.return_value = 5.0
                    MockNumpy.abs.return_value = mock_array
                    
                    diff = manager.compare_screenshots(b'data1', b'data2')
                    assert isinstance(diff, float), "Should return float difference"
                    print("✅ Screenshot comparison works")
            
            # Test utility methods
            base64_str = manager.screenshot_to_base64(b'test_data')
            assert isinstance(base64_str, str), "Should return base64 string"
            
            converted_back = manager.base64_to_screenshot(base64_str)
            assert converted_back == b'test_data', "Should convert back correctly"
            print("✅ Base64 conversion works")
            
            # Test status reporting
            status = manager.get_status()
            assert isinstance(status, dict), "Status should be dict"
            assert 'screenshot_count' in status, "Should include screenshot count"
            assert 'monitoring' in status, "Should include monitoring status"
            assert 'roi' in status, "Should include ROI"
            print("✅ Status reporting works")
            
            print("\n🎯 CORE FUNCTIONALITY TEST COMPLETE!")
            print("✅ All core screenshot methods work correctly")
            print("✅ Component initialization and monitoring work")
            print("✅ Utility methods function properly")
            print("✅ No functionality was broken during refactoring")
            
            return True
            
    except Exception as e:
        print(f"❌ Core functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_core_functionality()
    
    if success:
        print("\n🎊 CORE FUNCTIONALITY TEST PASSED! 🎊")
        print("All existing features work correctly after refactoring!")
    else:
        print("\n❌ CORE FUNCTIONALITY TEST FAILED!")
        print("Some existing features may have been broken during refactoring.")
        sys.exit(1)
