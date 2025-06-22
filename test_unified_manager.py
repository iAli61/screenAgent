#!/usr/bin/env python3
"""
Test the unified screenshot manager
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_unified_manager():
    """Test the unified screenshot manager"""
    print("🔍 Testing Unified Screenshot Manager...")
    
    try:
        from src.core.storage.screenshot_manager_unified import ScreenshotManager
        from src.core.config.config import Config
        
        print("✅ Imports successful")
        
        # Create config and manager
        config = Config()
        manager = ScreenshotManager(config)
        
        print("✅ Manager created")
        
        # Test initialization
        init_success = manager.initialize()
        print(f"✅ Initialization: {'Success' if init_success else 'Failed'}")
        
        if init_success:
            # Test status
            status = manager.get_status()
            print(f"✅ Status: {status.get('initialized', False)}")
            
            # Test screenshot count
            count = manager.get_screenshot_count()
            print(f"✅ Screenshot count: {count}")
            
            # Test cleanup
            manager.cleanup()
            print("✅ Cleanup successful")
        
        return init_success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_unified_manager()
    print(f"\n{'🎉 Test passed!' if success else '❌ Test failed!'}")
    sys.exit(0 if success else 1)
