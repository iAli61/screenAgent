#!/usr/bin/env python3
"""
Performance and functionality test for the unified screenshot capture module
Tests the consolidated implementation after removing duplicated code
"""
import time
import sys
import os
import traceback
from typing import Optional, Dict, Any

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from src.core.config import Config
    from src.core.capture.screenshot_capture import ScreenshotCaptureManager, ScreenshotCapture
    from src.utils.platform_detection import get_platform_info, get_recommended_screenshot_method
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class PerformanceTestResults:
    """Store and analyze performance test results"""
    
    def __init__(self):
        self.results = {}
    
    def add_result(self, test_name: str, implementation: str, 
                   duration: float, success: bool, data_size: int = 0, error: str = None):
        """Add a test result"""
        if test_name not in self.results:
            self.results[test_name] = {}
        
        self.results[test_name][implementation] = {
            'duration': duration,
            'success': success,
            'data_size': data_size,
            'error': error
        }
    
    def print_comparison(self):
        """Print performance comparison results"""
        print("\n" + "="*80)
        print("📊 PERFORMANCE COMPARISON RESULTS")
        print("="*80)
        
        for test_name, implementations in self.results.items():
            print(f"\n🧪 {test_name}")
            print("-" * 50)
            
            for impl_name, result in implementations.items():
                status = "✅" if result['success'] else "❌"
                duration_ms = result['duration'] * 1000
                size_kb = result['data_size'] / 1024 if result['data_size'] > 0 else 0
                
                print(f"  {status} {impl_name}:")
                print(f"     Duration: {duration_ms:.2f}ms")
                if result['success']:
                    print(f"     Data size: {size_kb:.1f}KB")
                else:
                    print(f"     Error: {result['error']}")
            
            # Performance comparison
            if len(implementations) == 2:
                impl_list = list(implementations.items())
                old_result = impl_list[0][1] if 'old' in impl_list[0][0].lower() else impl_list[1][1]
                new_result = impl_list[1][1] if 'new' in impl_list[1][0].lower() else impl_list[0][1]
                
                if old_result['success'] and new_result['success']:
                    speedup = old_result['duration'] / new_result['duration']
                    if speedup > 1.1:
                        print(f"     🚀 New implementation is {speedup:.1f}x faster")
                    elif speedup < 0.9:
                        print(f"     🐌 New implementation is {1/speedup:.1f}x slower")
                    else:
                        print(f"     ⚖️  Similar performance (ratio: {speedup:.2f})")


def test_initialization(config: Config, results: PerformanceTestResults):
    """Test initialization performance"""
    print("\n🔧 Testing Initialization Performance...")
    
    # Test old implementation
    start_time = time.time()
    try:
        old_capture = OldScreenshotCapture(config)
        old_success = old_capture.initialize()
        old_duration = time.time() - start_time
        results.add_result("Initialization", "Old Implementation", old_duration, old_success)
        print(f"  Old: {old_duration*1000:.2f}ms - {'✅' if old_success else '❌'}")
    except Exception as e:
        old_duration = time.time() - start_time
        results.add_result("Initialization", "Old Implementation", old_duration, False, error=str(e))
        print(f"  Old: ❌ Error - {e}")
    
    # Test new implementation
    start_time = time.time()
    try:
        new_manager = ScreenshotCaptureManager(config)
        new_success = new_manager.initialize()
        new_duration = time.time() - start_time
        results.add_result("Initialization", "New Implementation", new_duration, new_success)
        print(f"  New: {new_duration*1000:.2f}ms - {'✅' if new_success else '❌'}")
        
        if new_success:
            capabilities = new_manager.get_capabilities()
            print(f"  📋 Capabilities: {capabilities['summary']}")
        
        new_manager.cleanup()
    except Exception as e:
        new_duration = time.time() - start_time
        results.add_result("Initialization", "New Implementation", new_duration, False, error=str(e))
        print(f"  New: ❌ Error - {e}")


def test_full_screen_capture(config: Config, results: PerformanceTestResults):
    """Test full screen capture performance"""
    print("\n📸 Testing Full Screen Capture Performance...")
    
    # Test old implementation
    try:
        old_capture = OldScreenshotCapture(config)
        if old_capture.initialize():
            start_time = time.time()
            old_data = old_capture.capture_full_screen()
            old_duration = time.time() - start_time
            old_success = old_data is not None
            data_size = len(old_data) if old_data else 0
            results.add_result("Full Screen Capture", "Old Implementation", old_duration, old_success, data_size)
            print(f"  Old: {old_duration*1000:.2f}ms - {'✅' if old_success else '❌'} ({data_size/1024:.1f}KB)")
        else:
            results.add_result("Full Screen Capture", "Old Implementation", 0, False, error="Initialization failed")
            print("  Old: ❌ Initialization failed")
    except Exception as e:
        results.add_result("Full Screen Capture", "Old Implementation", 0, False, error=str(e))
        print(f"  Old: ❌ Error - {e}")
    
    # Test new implementation
    try:
        new_manager = ScreenshotCaptureManager(config)
        if new_manager.initialize():
            start_time = time.time()
            new_result = new_manager.capture_full_screen()
            new_duration = time.time() - start_time
            data_size = len(new_result.data) if new_result.success and new_result.data else 0
            results.add_result("Full Screen Capture", "New Implementation", new_duration, new_result.success, data_size)
            print(f"  New: {new_duration*1000:.2f}ms - {'✅' if new_result.success else '❌'} ({data_size/1024:.1f}KB)")
            if not new_result.success:
                print(f"       Error: {new_result.error}")
            new_manager.cleanup()
        else:
            results.add_result("Full Screen Capture", "New Implementation", 0, False, error="Initialization failed")
            print("  New: ❌ Initialization failed")
    except Exception as e:
        results.add_result("Full Screen Capture", "New Implementation", 0, False, error=str(e))
        print(f"  New: ❌ Error - {e}")


def test_roi_capture(config: Config, results: PerformanceTestResults):
    """Test ROI capture performance"""
    print("\n🎯 Testing ROI Capture Performance...")
    
    # Test ROI (200x200 region in upper left)
    test_roi = (100, 100, 300, 300)
    
    # Test old implementation
    try:
        old_capture = OldScreenshotCapture(config)
        if old_capture.initialize():
            start_time = time.time()
            old_data = old_capture.capture_roi(test_roi)
            old_duration = time.time() - start_time
            old_success = old_data is not None
            data_size = len(old_data) if old_data else 0
            results.add_result("ROI Capture", "Old Implementation", old_duration, old_success, data_size)
            print(f"  Old: {old_duration*1000:.2f}ms - {'✅' if old_success else '❌'} ({data_size/1024:.1f}KB)")
        else:
            results.add_result("ROI Capture", "Old Implementation", 0, False, error="Initialization failed")
            print("  Old: ❌ Initialization failed")
    except Exception as e:
        results.add_result("ROI Capture", "Old Implementation", 0, False, error=str(e))
        print(f"  Old: ❌ Error - {e}")
    
    # Test new implementation
    try:
        new_manager = ScreenshotCaptureManager(config)
        if new_manager.initialize():
            start_time = time.time()
            new_result = new_manager.capture_roi(test_roi)
            new_duration = time.time() - start_time
            data_size = len(new_result.data) if new_result.success and new_result.data else 0
            results.add_result("ROI Capture", "New Implementation", new_duration, new_result.success, data_size)
            print(f"  New: {new_duration*1000:.2f}ms - {'✅' if new_result.success else '❌'} ({data_size/1024:.1f}KB)")
            if not new_result.success:
                print(f"       Error: {new_result.error}")
            new_manager.cleanup()
        else:
            results.add_result("ROI Capture", "New Implementation", 0, False, error="Initialization failed")
            print("  New: ❌ Initialization failed")
    except Exception as e:
        results.add_result("ROI Capture", "New Implementation", 0, False, error=str(e))
        print(f"  New: ❌ Error - {e}")


def test_error_handling(config: Config, results: PerformanceTestResults):
    """Test error handling with invalid ROI"""
    print("\n🚨 Testing Error Handling...")
    
    # Invalid ROI (reversed coordinates)
    invalid_roi = (300, 300, 100, 100)
    
    # Test old implementation
    try:
        old_capture = OldScreenshotCapture(config)
        if old_capture.initialize():
            start_time = time.time()
            old_data = old_capture.capture_roi(invalid_roi)
            old_duration = time.time() - start_time
            old_success = old_data is not None
            # For error handling, we expect failure
            handled_correctly = not old_success
            results.add_result("Error Handling", "Old Implementation", old_duration, handled_correctly)
            print(f"  Old: {'✅' if handled_correctly else '❌'} - Handled invalid ROI correctly")
        else:
            results.add_result("Error Handling", "Old Implementation", 0, False, error="Initialization failed")
            print("  Old: ❌ Initialization failed")
    except Exception as e:
        # Exception is also correct error handling
        results.add_result("Error Handling", "Old Implementation", 0, True)
        print(f"  Old: ✅ Exception thrown for invalid ROI")
    
    # Test new implementation
    try:
        new_manager = ScreenshotCaptureManager(config)
        if new_manager.initialize():
            start_time = time.time()
            new_result = new_manager.capture_roi(invalid_roi)
            new_duration = time.time() - start_time
            # For error handling, we expect failure with error message
            handled_correctly = not new_result.success and new_result.error is not None
            results.add_result("Error Handling", "New Implementation", new_duration, handled_correctly)
            print(f"  New: {'✅' if handled_correctly else '❌'} - Handled invalid ROI correctly")
            if new_result.error:
                print(f"       Error message: {new_result.error}")
            new_manager.cleanup()
        else:
            results.add_result("Error Handling", "New Implementation", 0, False, error="Initialization failed")
            print("  New: ❌ Initialization failed")
    except Exception as e:
        results.add_result("Error Handling", "New Implementation", 0, False, error=str(e))
        print(f"  New: ❌ Unexpected exception - {e}")


def main():
    """Run performance tests"""
    print("🎯 ScreenAgent Screenshot Capture Refactoring Test")
    print("=" * 60)
    
    # Display platform information
    platform_info = get_platform_info()
    print("\n🖥️  Platform Information:")
    for key, value in platform_info.items():
        print(f"  {key}: {value}")
    
    print(f"\n📋 Recommended method: {get_recommended_screenshot_method()}")
    
    # Initialize configuration
    config = Config()
    results = PerformanceTestResults()
    
    try:
        # Run tests
        test_initialization(config, results)
        test_full_screen_capture(config, results)
        test_roi_capture(config, results)
        test_error_handling(config, results)
        
        # Print comparison results
        results.print_comparison()
        
        print("\n✅ Performance testing completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
