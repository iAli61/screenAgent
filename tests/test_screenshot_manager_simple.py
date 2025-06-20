#!/usr/bin/env python3
"""
Simplified test for Screenshot Manager Refactor (Phase 1.4)
Tests core functionality without external dependencies
"""
import sys
import os
import time
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from src.core.config import Config
        print("   ✅ Config imported")
    except Exception as e:
        print(f"   ❌ Config import failed: {e}")
        return False
    
    try:
        from src.core.storage_manager import StorageFactory, ScreenshotData, ScreenshotMetadata
        print("   ✅ Storage manager imported")
    except Exception as e:
        print(f"   ❌ Storage manager import failed: {e}")
        return False
    
    try:
        from src.core.events import EventDispatcher, subscribe_to_events, EventType
        print("   ✅ Events imported")
    except Exception as e:
        print(f"   ❌ Events import failed: {e}")
        return False
    
    try:
        from src.core.screenshot_capture_refactored import ScreenshotCaptureManager
        print("   ✅ Screenshot capture imported")
    except Exception as e:
        print(f"   ❌ Screenshot capture import failed: {e}")
        return False
    
    try:
        from src.core.roi_monitor_refactored import ROIMonitorManager
        print("   ✅ ROI monitor imported")
    except Exception as e:
        print(f"   ❌ ROI monitor import failed: {e}")
        return False
    
    try:
        from src.core.screenshot_orchestrator import ScreenshotOrchestrator
        print("   ✅ Screenshot orchestrator imported")
    except Exception as e:
        print(f"   ❌ Screenshot orchestrator import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        from src.core.screenshot_manager_refactored import ScreenshotManagerRefactored
        print("   ✅ Screenshot manager refactored imported")
    except Exception as e:
        print(f"   ❌ Screenshot manager refactored import failed: {e}")
        return False
    
    return True


def test_storage_manager():
    """Test storage manager functionality"""
    print("\n🧪 Testing storage manager...")
    
    from src.core.config import Config
    from src.core.storage_manager import StorageFactory, ScreenshotData, ScreenshotMetadata
    
    # Create test config
    config = Config()
    
    try:
        # Test in-memory storage
        storage = StorageFactory.create_memory_storage()
        print("   ✅ Storage created")
        
        # Create test data
        metadata = ScreenshotMetadata(
            id="test-001",
            timestamp=time.time(),
            timestamp_formatted="2024-01-01 12:00:00",
            size=1024,
            roi=(0, 0, 100, 100),
            capture_method="test",
            tags=["test"]
        )
        
        test_data = b"fake screenshot data"
        screenshot = ScreenshotData(metadata=metadata, data=test_data)
        
        # Test store
        if not storage.store_screenshot(screenshot):
            print("   ❌ Failed to store screenshot")
            return False
        print("   ✅ Screenshot stored")
        
        # Test retrieve
        retrieved = storage.retrieve_screenshot("test-001")
        if not retrieved or retrieved.data != test_data:
            print("   ❌ Failed to retrieve screenshot")
            return False
        print("   ✅ Screenshot retrieved")
        
        # Test list
        screenshots = storage.list_screenshots()
        if len(screenshots) != 1:
            print("   ❌ Failed to list screenshots")
            return False
        print("   ✅ Screenshots listed")
        
        # Test stats
        stats = storage.get_storage_stats()
        if stats['count'] != 1:
            print("   ❌ Invalid storage stats")
            return False
        print("   ✅ Storage stats correct")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Storage manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator_basic():
    """Test basic orchestrator functionality"""
    print("\n🧪 Testing orchestrator basic functionality...")
    
    from src.core.config import Config
    from src.core.screenshot_orchestrator import ScreenshotOrchestrator
    
    try:
        # Create test config
        config = Config()
        config.roi = (100, 100, 400, 300)
        
        # Create orchestrator
        orchestrator = ScreenshotOrchestrator(config)
        print("   ✅ Orchestrator created")
        
        # Test initialization
        success = orchestrator.initialize()
        print(f"   📊 Initialization result: {success}")
        
        # Test status (should work even if init failed)
        status = orchestrator.get_status()
        print(f"   📊 Status keys: {list(status.keys())}")
        
        if 'error' in status:
            print(f"   ⚠️  Status error: {status['error']}")
        
        # Test screenshots list (should be empty)
        screenshots = orchestrator.get_screenshots()
        if not isinstance(screenshots, list):
            print("   ❌ Screenshots should be a list")
            return False
        print(f"   ✅ Screenshots list: {len(screenshots)} items")
        
        # Cleanup
        orchestrator.cleanup()
        print("   ✅ Orchestrator cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Orchestrator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_screenshot_manager():
    """Test screenshot manager functionality"""
    print("\n🧪 Testing screenshot manager...")
    
    from src.core.config import Config
    from src.core.screenshot_manager_refactored import ScreenshotManagerRefactored
    
    try:
        # Create test config
        config = Config()
        config.roi = (100, 100, 400, 300)
        
        # Create manager
        manager = ScreenshotManagerRefactored(config)
        print("   ✅ Manager created")
        
        # Test initial state
        if manager.is_initialized():
            print("   ❌ Manager should not be initialized yet")
            return False
        print("   ✅ Initial state correct")
        
        # Test initialization
        success = manager.initialize()
        print(f"   📊 Initialization result: {success}")
        
        # Test screenshot count
        count = manager.get_screenshot_count()
        print(f"   📊 Screenshot count: {count}")
        
        # Test screenshots list
        screenshots = manager.get_screenshots()
        if not isinstance(screenshots, list):
            print("   ❌ Screenshots should be a list")
            return False
        print(f"   ✅ Screenshots list: {len(screenshots)} items")
        
        # Test status
        status = manager.get_status()
        if isinstance(status, dict):
            print(f"   ✅ Status returned: {len(status)} keys")
        else:
            print("   ❌ Status should be a dict")
            return False
        
        # Test compatibility methods
        all_screenshots = manager.get_all_screenshots()
        if not isinstance(all_screenshots, list):
            print("   ❌ get_all_screenshots should return a list")
            return False
        print("   ✅ Compatibility methods work")
        
        # Test has_screenshots
        has_screenshots = manager.has_screenshots()
        print(f"   📊 Has screenshots: {has_screenshots}")
        
        # Cleanup
        manager.cleanup()
        print("   ✅ Manager cleaned up")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Screenshot manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("🚀 Screenshot Manager Refactor - Simple Test Suite")
    print("   Testing Phase 1.4: Core functionality without external dependencies")
    
    tests = [
        ("Import Tests", test_imports),
        ("Storage Manager", test_storage_manager),
        ("Orchestrator Basic", test_orchestrator_basic),
        ("Screenshot Manager", test_screenshot_manager),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            if test_func():
                print(f"\n✅ {test_name} - PASSED")
                passed += 1
            else:
                print(f"\n❌ {test_name} - FAILED")
                failed += 1
        except Exception as e:
            print(f"\n❌ {test_name} - ERROR: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("Screenshot Manager refactor is working correctly.")
    else:
        print(f"\n❌ {failed} test(s) failed.")
    
    print('='*60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
