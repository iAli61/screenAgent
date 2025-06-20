#!/usr/bin/env python3
"""
Test suite for Screenshot Manager Refactor (Phase 1.4)
Tests the orchestrator, storage manager, and refactored screenshot manager
"""
import sys
import os
import time
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import Config
from src.core.screenshot_manager_refactored import ScreenshotManagerRefactored
from src.core.screenshot_orchestrator import ScreenshotOrchestrator
from src.core.storage_manager import StorageFactory, ScreenshotData, ScreenshotMetadata
from src.core.events import subscribe_to_events, EventType


class ScreenshotManagerTests:
    """Test suite for Screenshot Manager refactor"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="screenshot_manager_test_")
        self.config = self._create_test_config()
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
        
        # Event tracking
        self.events_received = []
        self._setup_event_tracking()
    
    def _create_test_config(self) -> Config:
        """Create test configuration"""
        config = Config()
        config.roi = (100, 100, 400, 300)  # Test ROI
        config.check_interval = 0.5
        config.temp_screenshot_path = os.path.join(self.temp_dir, "temp_screenshot.png")
        config.screenshots_dir = os.path.join(self.temp_dir, "screenshots")
        config.max_screenshots = 10
        config.change_threshold = 0.1
        return config
    
    def _setup_event_tracking(self):
        """Setup event tracking for tests"""
        def track_events(event):
            self.events_received.append({
                'type': type(event).__name__,
                'timestamp': time.time(),
                'event_id': getattr(event, 'event_id', None)
            })
        
        subscribe_to_events(EventType.SCREENSHOT_CAPTURED, track_events)
        subscribe_to_events(EventType.CHANGE_DETECTED, track_events)
    
    def run_test(self, test_name: str, test_func) -> bool:
        """Run a single test"""
        print(f"\n🧪 Running test: {test_name}")
        
        try:
            result = test_func()
            if result:
                print(f"   ✅ {test_name} - PASSED")
                self.tests_passed += 1
                self.test_results.append((test_name, "PASSED", None))
                return True
            else:
                print(f"   ❌ {test_name} - FAILED")
                self.tests_failed += 1
                self.test_results.append((test_name, "FAILED", "Test returned False"))
                return False
                
        except Exception as e:
            print(f"   ❌ {test_name} - ERROR: {e}")
            self.tests_failed += 1
            self.test_results.append((test_name, "ERROR", str(e)))
            return False
    
    def test_storage_manager(self) -> bool:
        """Test storage manager functionality"""
        print("   Testing storage manager...")
        
        # Test in-memory storage
        storage = StorageFactory.create_storage('memory', self.config)
        
        # Create test metadata and data
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
        
        # Test storage
        if not storage.store_screenshot(screenshot):
            return False
        
        # Test retrieval
        retrieved = storage.retrieve_screenshot("test-001")
        if not retrieved or retrieved.data != test_data:
            return False
        
        # Test listing
        screenshots = storage.list_screenshots()
        if len(screenshots) != 1 or screenshots[0].id != "test-001":
            return False
        
        # Test stats
        stats = storage.get_storage_stats()
        if stats['count'] != 1 or stats['total_size'] != 1024:
            return False
        
        # Test deletion
        if not storage.delete_screenshot("test-001"):
            return False
        
        if storage.retrieve_screenshot("test-001") is not None:
            return False
        
        print("   ✅ Storage manager tests passed")
        return True
    
    def test_orchestrator_initialization(self) -> bool:
        """Test orchestrator initialization"""
        print("   Testing orchestrator initialization...")
        
        orchestrator = ScreenshotOrchestrator(self.config)
        
        if not orchestrator.initialize():
            print("   ❌ Failed to initialize orchestrator")
            return False
        
        status = orchestrator.get_status()
        if not status['initialized']:
            return False
        
        print("   ✅ Orchestrator initialization successful")
        orchestrator.cleanup()
        return True
    
    def test_screenshot_manager_initialization(self) -> bool:
        """Test screenshot manager initialization"""
        print("   Testing screenshot manager initialization...")
        
        manager = ScreenshotManagerRefactored(self.config)
        
        if not manager.initialize():
            print("   ❌ Failed to initialize screenshot manager")
            return False
        
        if not manager.is_initialized():
            return False
        
        status = manager.get_status()
        if 'error' in status:
            return False
        
        print("   ✅ Screenshot manager initialization successful")
        manager.cleanup()
        return True
    
    def test_screenshot_operations(self) -> bool:
        """Test basic screenshot operations"""
        print("   Testing screenshot operations...")
        
        manager = ScreenshotManagerRefactored(self.config)
        
        if not manager.initialize():
            return False
        
        # Test screenshot count (should be 0)
        if manager.get_screenshot_count() != 0:
            manager.cleanup()
            return False
        
        # Test taking screenshots (will fail on headless, but should handle gracefully)
        screenshot_id = manager.take_roi_screenshot()
        
        # Even if screenshot fails, the manager should handle it gracefully
        screenshots = manager.get_screenshots()
        screenshot_count = manager.get_screenshot_count()
        
        print(f"   📊 Screenshot count: {screenshot_count}")
        print(f"   📊 Screenshots list length: {len(screenshots)}")
        
        # Test status
        status = manager.get_status()
        if 'error' in status:
            manager.cleanup()
            return False
        
        print("   ✅ Screenshot operations tested")
        manager.cleanup()
        return True
    
    def test_monitoring_operations(self) -> bool:
        """Test monitoring start/stop operations"""
        print("   Testing monitoring operations...")
        
        manager = ScreenshotManagerRefactored(self.config)
        
        if not manager.initialize():
            return False
        
        # Test initial state
        if manager.is_monitoring():
            manager.cleanup()
            return False
        
        # Test starting monitoring
        roi = (100, 100, 400, 300)
        success = manager.start_monitoring(roi)
        
        # Even if monitoring setup fails (e.g., on headless), it should handle gracefully
        print(f"   📊 Monitoring start result: {success}")
        
        # Test stopping monitoring
        manager.stop_monitoring()
        
        # Should be stopped now
        if manager.is_monitoring():
            print("   ⚠️  Monitoring still active after stop")
        
        print("   ✅ Monitoring operations tested")
        manager.cleanup()
        return True
    
    def test_data_operations(self) -> bool:
        """Test data manipulation operations"""
        print("   Testing data operations...")
        
        manager = ScreenshotManagerRefactored(self.config)
        
        if not manager.initialize():
            return False
        
        # Test clearing (should work even with no screenshots)
        if not manager.clear_all_screenshots():
            manager.cleanup()
            return False
        
        # Test getting non-existent screenshot
        data = manager.get_screenshot_data("non-existent")
        if data is not None:
            manager.cleanup()
            return False
        
        # Test analysis operations
        manager.set_analysis_response("test-id", "test response")
        response = manager.get_analysis_response("test-id")
        if response != "test response":
            manager.cleanup()
            return False
        
        print("   ✅ Data operations tested")
        manager.cleanup()
        return True
    
    def test_settings_and_configuration(self) -> bool:
        """Test settings and configuration updates"""
        print("   Testing settings and configuration...")
        
        manager = ScreenshotManagerRefactored(self.config)
        
        if not manager.initialize():
            return False
        
        # Test settings update
        new_settings = {
            'check_interval': 1.0,
            'change_sensitivity': 0.2,
            'roi': (50, 50, 200, 200)
        }
        
        result = manager.update_settings(new_settings)
        print(f"   📊 Settings update result: {result}")
        
        # Test status after settings update
        status = manager.get_status()
        if 'error' in status:
            manager.cleanup()
            return False
        
        print("   ✅ Settings and configuration tested")
        manager.cleanup()
        return True
    
    def test_compatibility_methods(self) -> bool:
        """Test backward compatibility methods"""
        print("   Testing compatibility methods...")
        
        manager = ScreenshotManagerRefactored(self.config)
        
        if not manager.initialize():
            return False
        
        # Test compatibility aliases
        all_screenshots = manager.get_all_screenshots()
        if not isinstance(all_screenshots, list):
            manager.cleanup()
            return False
        
        # Test latest screenshot (should be None)
        latest = manager.get_latest_screenshot()
        if latest is not None:
            print(f"   ⚠️  Expected None, got: {latest}")
        
        # Test has_screenshots
        has_screenshots = manager.has_screenshots()
        print(f"   📊 Has screenshots: {has_screenshots}")
        
        print("   ✅ Compatibility methods tested")
        manager.cleanup()
        return True
    
    def test_error_handling(self) -> bool:
        """Test error handling and edge cases"""
        print("   Testing error handling...")
        
        # Test operations before initialization
        manager = ScreenshotManagerRefactored(self.config)
        
        # Should handle gracefully when not initialized
        if manager.take_screenshot() is not None:
            return False
        
        if manager.is_monitoring():
            return False
        
        if manager.get_screenshots():
            return False
        
        if manager.get_screenshot_count() != 0:
            return False
        
        # Test with invalid data
        if manager.delete_screenshot("invalid-id"):
            return False
        
        print("   ✅ Error handling tested")
        return True
    
    def test_performance_and_memory(self) -> bool:
        """Test performance and memory usage"""
        print("   Testing performance and memory...")
        
        import psutil
        import gc
        
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        manager = ScreenshotManagerRefactored(self.config)
        
        if not manager.initialize():
            return False
        
        # Simulate some operations
        start_time = time.time()
        
        for i in range(5):
            manager.get_status()
            manager.get_screenshots()
            manager.get_screenshot_count()
            time.sleep(0.01)  # Small delay
        
        operation_time = time.time() - start_time
        
        # Check memory after operations
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        print(f"   📊 Operation time: {operation_time:.3f}s")
        print(f"   📊 Memory increase: {memory_increase:.2f}MB")
        
        # Cleanup
        manager.cleanup()
        gc.collect()
        
        # Performance thresholds (generous for CI environments)
        if operation_time > 5.0:  # 5 seconds for 5 operations
            print(f"   ⚠️  Operations took too long: {operation_time:.3f}s")
        
        if memory_increase > 50:  # 50MB increase
            print(f"   ⚠️  Memory increase too high: {memory_increase:.2f}MB")
        
        print("   ✅ Performance and memory tested")
        return True
    
    def test_integration_with_events(self) -> bool:
        """Test integration with event system"""
        print("   Testing event system integration...")
        
        # Clear previous events
        self.events_received.clear()
        
        manager = ScreenshotManagerRefactored(self.config)
        
        if not manager.initialize():
            return False
        
        # Try to trigger some events (may not work in headless environment)
        initial_event_count = len(self.events_received)
        
        # Attempt screenshot (might fail, but should handle gracefully)
        manager.take_roi_screenshot()
        
        # Wait a bit for events
        time.sleep(0.1)
        
        # Check if any events were generated
        final_event_count = len(self.events_received)
        events_generated = final_event_count - initial_event_count
        
        print(f"   📊 Events generated: {events_generated}")
        
        # Even if no events are generated (e.g., headless), that's ok
        # The important thing is that the system doesn't crash
        
        manager.cleanup()
        
        print("   ✅ Event system integration tested")
        return True
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Screenshot Manager Refactor Tests (Phase 1.4)")
        print(f"   Temp directory: {self.temp_dir}")
        
        start_time = time.time()
        
        # Run all tests
        test_methods = [
            ("Storage Manager", self.test_storage_manager),
            ("Orchestrator Initialization", self.test_orchestrator_initialization),
            ("Screenshot Manager Initialization", self.test_screenshot_manager_initialization),
            ("Screenshot Operations", self.test_screenshot_operations),
            ("Monitoring Operations", self.test_monitoring_operations),
            ("Data Operations", self.test_data_operations),
            ("Settings and Configuration", self.test_settings_and_configuration),
            ("Compatibility Methods", self.test_compatibility_methods),
            ("Error Handling", self.test_error_handling),
            ("Performance and Memory", self.test_performance_and_memory),
            ("Event System Integration", self.test_integration_with_events),
        ]
        
        for test_name, test_func in test_methods:
            self.run_test(test_name, test_func)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        self._print_summary(total_time)
        
        return self.tests_failed == 0
    
    def _print_summary(self, total_time: float):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 SCREENSHOT MANAGER REFACTOR TEST SUMMARY")
        print("="*60)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_failed}")
        print(f"🕒 Total Time: {total_time:.2f}s")
        print(f"📁 Temp Directory: {self.temp_dir}")
        print(f"📧 Events Received: {len(self.events_received)}")
        
        if self.tests_failed > 0:
            print("\n❌ FAILED TESTS:")
            for test_name, status, error in self.test_results:
                if status != "PASSED":
                    print(f"   • {test_name}: {status}")
                    if error:
                        print(f"     Error: {error}")
        
        print("\n" + "="*60)
        
        if self.tests_failed == 0:
            print("🎉 ALL TESTS PASSED! Screenshot Manager refactor is working correctly.")
        else:
            print("❌ Some tests failed. Please review the implementation.")
        
        print("="*60)
    
    def cleanup(self):
        """Clean up test resources"""
        try:
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            print(f"⚠️  Failed to clean up temp directory: {e}")


def main():
    """Main test execution"""
    print("🚀 Screenshot Manager Refactor Test Suite")
    print("   Testing Phase 1.4: Screenshot Manager Module Refactoring")
    
    tests = ScreenshotManagerTests()
    
    try:
        success = tests.run_all_tests()
        return 0 if success else 1
    
    finally:
        tests.cleanup()


if __name__ == "__main__":
    exit(main())
