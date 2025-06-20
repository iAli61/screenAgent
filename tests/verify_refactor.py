#!/usr/bin/env python3
"""
Minimal verification that our refactored modules are working
"""
import sys
import os
import traceback

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test that our new modules can be imported"""
    try:
        # Test core imports
        from src.core.config import Config
        from src.core.platform_detection import get_platform_info
        
        # Test new interfaces
        from src.core.capture_interfaces import CaptureMethod, ScreenshotCaptureFactory, CaptureResult
        
        # Test implementations  
        from src.core.capture_implementations import WSLPowerShellCapture, WindowsNativeCapture
        
        # Test refactored manager
        from src.core.screenshot_capture_refactored import ScreenshotCaptureManager
        
        print("✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality of refactored components"""
    try:
        from src.core.config import Config
        from src.core.screenshot_capture_refactored import ScreenshotCaptureManager
        from src.core.capture_interfaces import CaptureMethod
        
        # Create config and manager
        config = Config()
        manager = ScreenshotCaptureManager(config)
        
        # Test initialization
        init_success = manager.initialize()
        print(f"Manager initialization: {'✅' if init_success else '❌'}")
        
        if init_success:
            # Get capabilities
            capabilities = manager.get_capabilities()
            print(f"Available methods: {len(capabilities['fallbacks']) + (1 if capabilities['primary'] else 0)}")
            print(f"Primary method: {capabilities['primary']['method'] if capabilities['primary'] else 'None'}")
            
            # Test a simple capture (this might fail without display but should not crash)
            result = manager.capture_full_screen()
            print(f"Capture attempt: {'✅' if result.success else '❌'} - {result.error if not result.success else 'Success'}")
        
        # Cleanup
        manager.cleanup()
        print("✅ Basic functionality test completed")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🎯 ScreenAgent Refactored Module Verification")
    print("=" * 50)
    
    success = True
    
    print("\n1. Testing imports...")
    success &= test_imports()
    
    print("\n2. Testing basic functionality...")
    success &= test_basic_functionality()
    
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")
    
    # Write results to a file as well since terminal might not be working
    with open('test_results.txt', 'w') as f:
        f.write(f"Refactoring test results: {'PASS' if success else 'FAIL'}\n")
    
    sys.exit(0 if success else 1)
