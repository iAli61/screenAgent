#!/usr/bin/env python3
print("🚀 Starting Screenshot Manager Phase 1.4 Test")

import sys
import os
sys.path.insert(0, 'src')

def test_basic_functionality():
    """Test basic functionality without hanging"""
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Config import
    try:
        from src.core.config import Config
        config = Config()
        config.roi = (100, 100, 400, 300)
        print("✅ Test 1: Config - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: Config - FAILED: {e}")
        tests_failed += 1
    
    # Test 2: Storage Manager
    try:
        from src.core.storage_manager import StorageFactory, ScreenshotData, ScreenshotMetadata
        import time
        
        storage = StorageFactory.create_memory_storage()
        
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
        
        # Test operations
        storage.store_screenshot(screenshot)
        retrieved = storage.retrieve_screenshot("test-001")
        stats = storage.get_storage_stats()
        
        if retrieved and retrieved.data == test_data and stats['count'] == 1:
            print("✅ Test 2: Storage Manager - PASSED")
            tests_passed += 1
        else:
            print("❌ Test 2: Storage Manager - FAILED: Data mismatch")
            tests_failed += 1
            
    except Exception as e:
        print(f"❌ Test 2: Storage Manager - FAILED: {e}")
        tests_failed += 1
    
    # Test 3: Screenshot Manager Refactored (without initialization)
    try:
        from src.core.screenshot_manager_refactored import ScreenshotManagerRefactored
        
        manager = ScreenshotManagerRefactored(config)
        
        # Test without initialization (should handle gracefully)
        if not manager.is_initialized():
            if manager.get_screenshot_count() == 0:
                if not manager.get_screenshots():
                    print("✅ Test 3: Screenshot Manager - PASSED")
                    tests_passed += 1
                else:
                    print("❌ Test 3: Screenshot Manager - FAILED: Should return empty list")
                    tests_failed += 1
            else:
                print("❌ Test 3: Screenshot Manager - FAILED: Count should be 0")
                tests_failed += 1
        else:
            print("❌ Test 3: Screenshot Manager - FAILED: Should not be initialized")
            tests_failed += 1
            
    except Exception as e:
        print(f"❌ Test 3: Screenshot Manager - FAILED: {e}")
        tests_failed += 1
    
    return tests_passed, tests_failed

if __name__ == "__main__":
    passed, failed = test_basic_functionality()
    
    print("\n" + "="*50)
    print(f"📊 Tests Passed: {passed}")
    print(f"❌ Tests Failed: {failed}")
    
    if failed == 0:
        print("🎉 ALL BASIC TESTS PASSED!")
        print("Phase 1.4 core components are working.")
    else:
        print(f"❌ {failed} test(s) failed.")
    
    print("="*50)
    
    exit(0 if failed == 0 else 1)
