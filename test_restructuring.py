#!/usr/bin/env python3
"""
Test the restructured file organization
Verify that all modules can be imported correctly after restructuring
"""
import sys
import os

print("🧪 Testing Restructured File Organization")
print("="*50)

def test_core_imports():
    """Test core module imports"""
    print("\n📦 Testing Core Module Imports:")
    
    try:
        from src.core.config import Config
        print("   ✅ Config import successful")
        
        from src.core.capture import ScreenshotCaptureManager, CaptureResult
        print("   ✅ Capture module import successful")
        
        from src.core.monitoring import ROIMonitorManager, ChangeResult  
        print("   ✅ Monitoring module import successful")
        
        from src.core.storage import ScreenshotOrchestrator, StorageFactory
        print("   ✅ Storage module import successful")
        
        from src.core.events import EventDispatcher, emit_event
        print("   ✅ Events module import successful")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Core import failed: {e}")
        return False

def test_utils_imports():
    """Test utils module imports"""
    print("\n🔧 Testing Utils Module Imports:")
    
    try:
        from src.utils import get_platform, KeyboardHandler
        print("   ✅ Utils import successful")
        return True
        
    except ImportError as e:
        print(f"   ❌ Utils import failed: {e}")
        return False

def test_api_imports():
    """Test API module imports"""
    print("\n🌐 Testing API Module Imports:")
    
    try:
        from src.api.server import RequestHandler
        print("   ✅ API server import successful")
        return True
        
    except ImportError as e:
        print(f"   ❌ API import failed: {e}")
        return False

def test_functionality():
    """Test basic functionality with new imports"""
    print("\n⚙️  Testing Basic Functionality:")
    
    try:
        from src.core.config import Config
        from src.core.storage import StorageFactory
        
        config = Config()
        storage = StorageFactory.create_memory_storage()
        stats = storage.get_storage_stats()
        
        print(f"   ✅ Storage created: {stats['count']} screenshots")
        print(f"   ✅ Config created: ROI = {config.roi}")
        return True
        
    except Exception as e:
        print(f"   ❌ Functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    tests = [
        ("Core Imports", test_core_imports),
        ("Utils Imports", test_utils_imports),
        ("API Imports", test_api_imports),
        ("Basic Functionality", test_functionality)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ❌ {test_name} crashed: {e}")
            failed += 1
    
    print("\n" + "="*50)
    print("📊 RESTRUCTURING TEST RESULTS")
    print("="*50)
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("File restructuring was successful.")
        print("All modules can be imported correctly.")
    else:
        print(f"\n❌ {failed} test(s) failed.")
        print("Some imports may need adjustment.")
    
    print("="*50)
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
