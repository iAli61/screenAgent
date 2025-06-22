#!/usr/bin/env python3
"""
Comprehensive test for the unified screenshot manager
Tests all functionality and measures performance
"""
import sys
import os
import time

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_comprehensive_functionality():
    """Test all unified manager functionality"""
    print("🎯 Comprehensive Unified Screenshot Manager Test")
    print("=" * 60)
    
    try:
        from src.core.storage.screenshot_manager_unified import ScreenshotManager
        from src.core.config.config import Config
        
        # Create manager
        config = Config()
        config.roi = (100, 100, 400, 400)  # Set test ROI
        manager = ScreenshotManager(config)
        
        print("✅ Manager created")
        
        # Test 1: Initialization
        print("\n1. Testing Initialization...")
        start_time = time.time()
        init_success = manager.initialize()
        init_duration = time.time() - start_time
        print(f"   Initialization: {init_duration:.2f}s - {'✅' if init_success else '❌'}")
        
        if not init_success:
            return False
        
        # Test 2: Status and capabilities
        print("\n2. Testing Status...")
        status = manager.get_status()
        print(f"   Initialized: {status.get('initialized')}")
        print(f"   Capture method: {status.get('capture_method')}")
        print(f"   Fallback methods: {status.get('fallback_methods')}")
        print(f"   Screenshot count: {status.get('screenshot_count')}")
        
        # Test 3: Full screenshot
        print("\n3. Testing Full Screenshot...")
        start_time = time.time()
        full_screenshot = manager.take_full_screenshot()
        full_duration = time.time() - start_time
        
        full_success = full_screenshot is not None
        full_size = len(full_screenshot) if full_screenshot else 0
        print(f"   Full screenshot: {full_duration:.2f}s - {'✅' if full_success else '❌'} ({full_size/1024:.1f}KB)")
        
        # Test 4: ROI screenshot
        print("\n4. Testing ROI Screenshot...")
        start_time = time.time()
        roi_screenshot = manager.take_roi_screenshot()
        roi_duration = time.time() - start_time
        
        roi_success = roi_screenshot is not None
        roi_size = len(roi_screenshot) if roi_screenshot else 0
        print(f"   ROI screenshot: {roi_duration:.2f}s - {'✅' if roi_success else '❌'} ({roi_size/1024:.1f}KB)")
        
        # Test 5: Unified ROI screenshot
        print("\n5. Testing Unified ROI Screenshot...")
        start_time = time.time()
        unified_roi = manager.take_unified_roi_screenshot()
        unified_duration = time.time() - start_time
        
        unified_success = unified_roi is not None
        unified_size = len(unified_roi) if unified_roi else 0
        print(f"   Unified ROI: {unified_duration:.2f}s - {'✅' if unified_success else '❌'} ({unified_size/1024:.1f}KB)")
        
        # Test 6: Screenshot collection management
        print("\n6. Testing Screenshot Collection...")
        if full_screenshot:
            manager.add_screenshot("test_full", full_screenshot, {"type": "full"})
        if roi_screenshot:
            manager.add_screenshot("test_roi", roi_screenshot, {"type": "roi"})
        
        count = manager.get_screenshot_count()
        all_screenshots = manager.get_all_screenshots()
        latest = manager.get_latest_screenshot()
        
        print(f"   Collection count: {count}")
        print(f"   All screenshots: {len(all_screenshots)}")
        print(f"   Latest screenshot: {'✅' if latest else '❌'}")
        
        # Test 7: Utility functions
        print("\n7. Testing Utility Functions...")
        if full_screenshot:
            # Test base64 conversion
            base64_data = manager.screenshot_to_base64(full_screenshot)
            back_to_bytes = manager.base64_to_screenshot(base64_data)
            base64_success = len(back_to_bytes) == len(full_screenshot)
            print(f"   Base64 conversion: {'✅' if base64_success else '❌'}")
            
            # Test resize
            resized = manager.resize_screenshot(full_screenshot, 800, 600)
            resize_success = len(resized) > 0
            print(f"   Screenshot resize: {'✅' if resize_success else '❌'} ({len(resized)/1024:.1f}KB)")
        
        # Test 8: Memory management
        print("\n8. Testing Memory Management...")
        memory_usage = manager.get_memory_usage()
        print(f"   Memory usage: {memory_usage.get('total_size_mb', 0):.2f}MB")
        print(f"   Usage percentage: {memory_usage.get('usage_percentage', 0):.1f}%")
        
        clear_success = manager.clear_all_screenshots()
        print(f"   Clear screenshots: {'✅' if clear_success else '❌'}")
        
        # Test 9: Cleanup
        print("\n9. Testing Cleanup...")
        manager.cleanup()
        print("   ✅ Cleanup completed")
        
        # Summary
        tests_passed = [
            init_success,
            full_success,
            roi_success,
            unified_success,
            count > 0,
            latest is not None,
            clear_success
        ]
        
        passed_count = sum(tests_passed)
        total_tests = len(tests_passed)
        
        print(f"\n{'=' * 60}")
        print(f"Test Results: {passed_count}/{total_tests} passed")
        
        if passed_count == total_tests:
            print("🎉 All tests passed! Unified manager is working perfectly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the output above.")
            return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_comprehensive_functionality()
    sys.exit(0 if success else 1)
