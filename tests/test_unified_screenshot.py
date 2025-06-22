#!/usr/bin/env python3
"""
Test for the unified screenshot capture module
Tests the consolidated implementation after removing duplicated code
"""
import time
import sys
import os
import traceback
from typing import Optional

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

try:
    from src.core.config import Config
    from src.core.capture.screenshot_capture import ScreenshotCaptureManager, ScreenshotCapture
    from src.utils.platform_detection import get_platform_info, get_recommended_screenshot_method
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def test_screenshot_manager():
    """Test the unified ScreenshotCaptureManager"""
    print("\n📸 Testing Unified ScreenshotCaptureManager...")
    
    config = Config()
    manager = ScreenshotCaptureManager(config)
    
    # Test initialization
    start_time = time.time()
    init_success = manager.initialize()
    init_duration = time.time() - start_time
    
    print(f"  Initialization: {init_duration*1000:.2f}ms - {'✅' if init_success else '❌'}")
    
    if not init_success:
        return False
    
    # Test capabilities
    capabilities = manager.get_capabilities()
    print(f"  Primary method: {capabilities.get('primary', {}).get('method', 'None')}")
    print(f"  Fallback methods: {len(capabilities.get('fallbacks', []))}")
    
    # Test full screen capture
    start_time = time.time()
    result = manager.capture_full_screen()
    capture_duration = time.time() - start_time
    
    success = result.success
    data_size = len(result.data) if result.data else 0
    
    print(f"  Full screen: {capture_duration*1000:.2f}ms - {'✅' if success else '❌'} ({data_size/1024:.1f}KB)")
    
    if success:
        # Test ROI capture
        test_roi = (100, 100, 300, 300)
        start_time = time.time()
        roi_result = manager.capture_roi(test_roi)
        roi_duration = time.time() - start_time
        
        roi_success = roi_result.success
        roi_size = len(roi_result.data) if roi_result.data else 0
        
        print(f"  ROI capture: {roi_duration*1000:.2f}ms - {'✅' if roi_success else '❌'} ({roi_size/1024:.1f}KB)")
    
    # Cleanup
    manager.cleanup()
    return init_success


def test_backward_compatibility():
    """Test the backward compatibility wrapper"""
    print("\n🔄 Testing Backward Compatibility Wrapper...")
    
    config = Config()
    capture = ScreenshotCapture(config)
    
    # Test initialization
    init_success = capture.initialize()
    print(f"  Wrapper init: {'✅' if init_success else '❌'}")
    
    if init_success:
        print(f"  Method: {capture.method}")
        
        # Test full screen capture
        start_time = time.time()
        data = capture.capture_full_screen()
        duration = time.time() - start_time
        
        success = data is not None
        size = len(data) if data else 0
        
        print(f"  Full screen: {duration*1000:.2f}ms - {'✅' if success else '❌'} ({size/1024:.1f}KB)")
        
        if success:
            # Test ROI capture
            test_roi = (100, 100, 300, 300)
            start_time = time.time()
            roi_data = capture.capture_roi(test_roi)
            roi_duration = time.time() - start_time
            
            roi_success = roi_data is not None
            roi_size = len(roi_data) if roi_data else 0
            
            print(f"  ROI capture: {roi_duration*1000:.2f}ms - {'✅' if roi_success else '❌'} ({roi_size/1024:.1f}KB)")
    
    # Cleanup
    capture.cleanup()
    return init_success


def test_legacy_functions():
    """Test legacy standalone functions"""
    print("\n🔧 Testing Legacy Functions...")
    
    # Test take_screenshot
    from src.core.capture.screenshot_capture import take_screenshot, take_full_screenshot
    
    start_time = time.time()
    data = take_screenshot()
    duration = time.time() - start_time
    
    success = data is not None
    size = len(data) if data else 0
    
    print(f"  take_screenshot(): {duration*1000:.2f}ms - {'✅' if success else '❌'} ({size/1024:.1f}KB)")
    
    # Test take_full_screenshot
    start_time = time.time()
    data = take_full_screenshot()
    duration = time.time() - start_time
    
    success = data is not None
    size = len(data) if data else 0
    
    print(f"  take_full_screenshot(): {duration*1000:.2f}ms - {'✅' if success else '❌'} ({size/1024:.1f}KB)")
    
    return True


def main():
    """Run all tests"""
    print("🎯 Testing Unified Screenshot Capture Module")
    print("=" * 50)
    
    # Show platform info
    try:
        platform_info = get_platform_info()
        recommended_method = get_recommended_screenshot_method()
        print(f"Platform: {platform_info}")
        print(f"Recommended method: {recommended_method}")
    except Exception as e:
        print(f"Platform detection error: {e}")
    
    tests = [
        test_screenshot_manager,
        test_backward_compatibility,
        test_legacy_functions
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} error: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Screenshot module is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
