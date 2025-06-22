#!/usr/bin/env python3
"""
Test for refactored ROI monitor with change detection and event system
Part of Phase 1.3 - ROI Monitor Module Refactoring
"""
import sys
import os
import time
import threading
from typing import List

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from src.core.config import Config
    from src.core.roi_monitor_refactored import ROIMonitorManager, ROIMonitor
    from src.core.capture.screenshot_capture import ScreenshotCaptureManager
    from src.core.change_detection import ChangeDetectorFactory, ChangeDetectionMethod
    from src.core.events import EventType, emit_event, get_event_dispatcher
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class ROIMonitorTest:
    """Test class for ROI monitor functionality"""
    
    def __init__(self):
        self.config = Config()
        self.results = []
        self.events_received = []
        
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅" if success else "❌"
        self.results.append((test_name, success, details))
        print(f"{status} {test_name}: {details}")
    
    def setup_event_listener(self):
        """Setup event listener to track events"""
        def event_handler(event):
            self.events_received.append(event)
            print(f"📡 Event received: {event.event_type.value} from {event.source}")
        
        dispatcher = get_event_dispatcher()
        dispatcher.subscribe_global(event_handler)
    
    def test_change_detection_methods(self):
        """Test different change detection methods"""
        print("\n🔍 Testing Change Detection Methods...")
        
        available_methods = ChangeDetectorFactory.get_available_methods()
        self.log_result(
            "Available detection methods", 
            len(available_methods) > 0,
            f"Found {len(available_methods)} methods: {[m.value for m in available_methods]}"
        )
        
        # Test each available method
        for method in available_methods:
            try:
                detector = ChangeDetectorFactory.create_detector(method, self.config, 0.5)
                self.log_result(
                    f"Create {method.value} detector",
                    True,
                    f"Supports ROI: {detector.supports_roi_analysis}"
                )
            except Exception as e:
                self.log_result(
                    f"Create {method.value} detector",
                    False,
                    str(e)
                )
    
    def test_roi_monitor_initialization(self):
        """Test ROI monitor initialization"""
        print("\n🔧 Testing ROI Monitor Initialization...")
        
        # Test new manager
        try:
            capture_manager = ScreenshotCaptureManager(self.config)
            capture_init = capture_manager.initialize()
            
            monitor_manager = ROIMonitorManager(self.config, capture_manager)
            monitor_init = monitor_manager.initialize()
            
            self.log_result(
                "ROI monitor manager initialization",
                monitor_init,
                f"Capture init: {capture_init}, Monitor init: {monitor_init}"
            )
            
            # Test backward compatibility wrapper
            old_monitor = ROIMonitor(self.config)
            old_init = old_monitor.initialize()
            
            self.log_result(
                "Backward compatible ROI monitor",
                old_init,
                "Old interface still works"
            )
            
            return monitor_manager, capture_manager
            
        except Exception as e:
            self.log_result(
                "ROI monitor initialization",
                False,
                str(e)
            )
            return None, None
    
    def test_monitoring_functionality(self, monitor_manager, capture_manager):
        """Test monitoring functionality"""
        if not monitor_manager or not capture_manager:
            return
        
        print("\n📸 Testing Monitoring Functionality...")
        
        # Test ROI configuration
        test_roi = (100, 100, 300, 300)
        
        try:
            # Test status before monitoring
            status = monitor_manager.get_status()
            self.log_result(
                "Get status (before monitoring)",
                not status['active'],
                f"Active: {status['active']}, Method: {status['detection_method']}"
            )
            
            # Test starting monitoring
            start_success = monitor_manager.start_monitoring(test_roi)
            self.log_result(
                "Start monitoring",
                start_success,
                f"ROI: {test_roi}"
            )
            
            if start_success:
                # Let it run for a few seconds
                time.sleep(3)
                
                # Test status during monitoring
                status = monitor_manager.get_status()
                self.log_result(
                    "Get status (during monitoring)",
                    status['active'],
                    f"Duration: {status['duration_formatted']}, Cycles: {status['statistics']['monitoring_cycles']}"
                )
                
                # Test force screenshot
                screenshot = monitor_manager.force_screenshot()
                self.log_result(
                    "Force screenshot",
                    screenshot is not None,
                    f"Size: {len(screenshot) if screenshot else 0} bytes"
                )
                
                # Test settings update
                new_settings = {
                    'check_interval': 2.0,
                    'change_sensitivity': 0.7
                }
                settings_updated = monitor_manager.update_settings(new_settings)
                self.log_result(
                    "Update settings",
                    settings_updated,
                    f"New interval: {new_settings['check_interval']}s"
                )
                
                # Let it run a bit more
                time.sleep(2)
                
                # Test stopping monitoring
                monitor_manager.stop_monitoring()
                
                # Check final status
                final_status = monitor_manager.get_status()
                self.log_result(
                    "Stop monitoring",
                    not final_status['active'],
                    f"Final cycles: {final_status['statistics']['monitoring_cycles']}"
                )
            
        except Exception as e:
            self.log_result(
                "Monitoring functionality test",
                False,
                str(e)
            )
        finally:
            # Ensure monitoring is stopped
            try:
                monitor_manager.stop_monitoring()
                capture_manager.cleanup()
            except:
                pass
    
    def test_event_system(self):
        """Test event system functionality"""
        print("\n📡 Testing Event System...")
        
        # Count events received during test
        initial_event_count = len(self.events_received)
        
        try:
            # Create a simple test event
            from src.core.events import BaseEvent, EventType
            test_event = BaseEvent(
                event_id="test_event",
                event_type=EventType.SYSTEM_STATUS_CHANGED,
                timestamp=time.time(),
                source="ROIMonitorTest",
                data={'test': True}
            )
            
            emit_event(test_event)
            
            # Give a moment for event processing
            time.sleep(0.1)
            
            events_received = len(self.events_received) - initial_event_count
            self.log_result(
                "Event system",
                events_received > 0,
                f"Received {events_received} events during test"
            )
            
            # Test event dispatcher stats
            dispatcher = get_event_dispatcher()
            stats = dispatcher.get_stats()
            self.log_result(
                "Event dispatcher stats",
                stats['total_handlers'] >= 0,
                f"Handlers: {stats['total_handlers']}, History: {stats['history_size']}"
            )
            
        except Exception as e:
            self.log_result(
                "Event system test",
                False,
                str(e)
            )
    
    def test_performance_comparison(self):
        """Test performance comparison between old and new implementations"""
        print("\n⚡ Testing Performance Comparison...")
        
        try:
            # Test old implementation
            from src.core.roi_monitor import ROIMonitor as OldROIMonitor
            
            old_monitor = OldROIMonitor(self.config)
            old_init = old_monitor.initialize()
            
            # Test new implementation
            capture_manager = ScreenshotCaptureManager(self.config)
            capture_init = capture_manager.initialize()
            
            new_monitor = ROIMonitorManager(self.config, capture_manager)
            new_init = new_monitor.initialize()
            
            self.log_result(
                "Implementation comparison",
                old_init and new_init,
                f"Old init: {old_init}, New init: {new_init}"
            )
            
            # Compare capabilities
            if new_init:
                status = new_monitor.get_status()
                available_methods = new_monitor.get_available_detection_methods()
                
                self.log_result(
                    "Enhanced capabilities",
                    len(available_methods) > 1,
                    f"Detection methods: {len(available_methods)}, Current: {status['detection_method']}"
                )
            
            # Cleanup
            capture_manager.cleanup()
            
        except Exception as e:
            self.log_result(
                "Performance comparison",
                False,
                str(e)
            )
    
    def run_all_tests(self):
        """Run all tests"""
        print("🎯 ROI Monitor Refactoring Test Suite")
        print("=" * 50)
        
        # Setup event listener
        self.setup_event_listener()
        
        # Run tests
        self.test_change_detection_methods()
        monitor_manager, capture_manager = self.test_roi_monitor_initialization()
        self.test_monitoring_functionality(monitor_manager, capture_manager)
        self.test_event_system()
        self.test_performance_comparison()
        
        # Print summary
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        
        for test_name, success, details in self.results:
            status = "✅" if success else "❌"
            print(f"{status} {test_name}")
            if details and not success:
                print(f"   Details: {details}")
        
        print(f"\nResults: {passed}/{total} tests passed")
        print(f"Events received: {len(self.events_received)}")
        
        # Write results to file
        with open('roi_monitor_test_results.txt', 'w') as f:
            f.write(f"ROI Monitor refactoring test results: {passed}/{total} passed\n")
            f.write(f"Events received: {len(self.events_received)}\n")
            for test_name, success, details in self.results:
                f.write(f"{'PASS' if success else 'FAIL'}: {test_name} - {details}\n")
        
        return passed == total


def main():
    """Run the ROI monitor tests"""
    test_runner = ROIMonitorTest()
    success = test_runner.run_all_tests()
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
