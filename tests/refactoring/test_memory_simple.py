#!/usr/bin/env python3
"""
Simple integration test for ScreenshotManager memory functionality
"""

import sys
import os
import tempfile
import shutil

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_memory_management():
    """Test the memory management functionality directly"""
    print("🚀 Testing ScreenshotManager memory management...")
    
    # Create a simple mock config
    class MockConfig:
        def __init__(self):
            self.temp_dir = tempfile.mkdtemp()
            self.temp_screenshot_path = os.path.join(self.temp_dir, 'temp.png')
            self.roi = (100, 100, 200, 200)
            self.change_threshold = 10.0
            self.check_interval = 1.0
            self.llm_enabled = True
            
        def get(self, key, default=None):
            config_values = {
                'max_screenshots': 3,  # Small limit for testing
                'auto_cleanup': True,
                'change_threshold': 10.0,
                'check_interval': 1.0,
                'llm_enabled': True
            }
            return config_values.get(key, default)
            
        def cleanup(self):
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    config = MockConfig()
    
    try:
        # Import and create a minimal manager for testing memory only
        from src.core.storage.screenshot_manager import ScreenshotManager
        
        # Create manager
        manager = ScreenshotManager.__new__(ScreenshotManager)  # Don't call __init__ to avoid component initialization
        manager.config = config
        manager._monitoring = False
        manager._max_screenshots = config.get('max_screenshots', 100)
        
        # Initialize memory manually
        manager._initialize_memory()
        
        print("✅ Created manager with clean memory")
        
        # Test 1: Initial state
        assert manager.get_screenshot_count() == 0, "Should start with 0 screenshots"
        memory_usage = manager.get_memory_usage()
        assert memory_usage['screenshot_count'] == 0, "Memory usage should show 0"
        print("✅ Initial state test passed")
        
        # Test 2: Add screenshots
        test_data = b'test_screenshot_data'
        for i in range(5):  # Add more than limit
            manager.add_screenshot(f"2025-06-21_{i:02d}:00:00", test_data, {'test': i})
        
        # Should be limited by max_screenshots (3)
        count = manager.get_screenshot_count()
        print(f"📊 Screenshots after adding 5: {count} (max: {manager._max_screenshots})")
        assert count == 3, f"Should be limited to 3, got {count}"
        print("✅ Memory limit test passed")
        
        # Test 3: LLM responses
        manager.set_llm_response(0, "Response 0")
        manager.set_llm_response(2, "Response 2")
        
        assert manager.get_llm_response(0) == "Response 0", "Response 0 should match"
        assert manager.get_llm_response(1) is None, "Response 1 should be None"
        assert manager.get_llm_response(2) == "Response 2", "Response 2 should match"
        print("✅ LLM response test passed")
        
        # Test 4: get_all_screenshots
        all_screenshots = manager.get_all_screenshots()
        assert len(all_screenshots) == 3, f"Should have 3 screenshots, got {len(all_screenshots)}"
        
        # Check LLM responses in all_screenshots
        assert all_screenshots[0]['llm_response'] == "Response 0", f"First should have 'Response 0', got: {all_screenshots[0]['llm_response']}"
        assert all_screenshots[1]['llm_response'] is None, f"Second should be None, got: {all_screenshots[1]['llm_response']}"
        assert all_screenshots[2]['llm_response'] == "Response 2", f"Third should have 'Response 2', got: {all_screenshots[2]['llm_response']}"
        print("✅ get_all_screenshots test passed")
        
        # Test 5: Clear all
        result = manager.clear_all_screenshots()
        assert result == True, "Clear should return True"
        assert manager.get_screenshot_count() == 0, "Should have 0 after clear"
        assert len(manager._llm_responses) == 0, "LLM responses should be cleared"
        print("✅ Clear all test passed")
        
        # Test 6: Memory usage reporting
        manager.add_screenshot("test", test_data)
        manager.set_llm_response(0, "test")
        usage = manager.get_memory_usage()
        
        assert usage['screenshot_count'] == 1, "Should show 1 screenshot"
        assert usage['total_size_bytes'] > 0, "Should show size > 0"
        assert usage['llm_responses_count'] == 1, "Should show 1 LLM response"
        print("✅ Memory usage reporting test passed")
        
        # Test 7: Cleanup
        manager.cleanup()
        assert manager.get_screenshot_count() == 0, "Cleanup should clear screenshots"
        print("✅ Cleanup test passed")
        
        print("\n🎉 All memory management tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        config.cleanup()

if __name__ == "__main__":
    success = test_memory_management()
    if success:
        print("\n✅ ScreenshotManager memory management is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ ScreenshotManager memory management has issues!")
        sys.exit(1)
