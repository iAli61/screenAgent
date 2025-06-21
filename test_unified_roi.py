#!/usr/bin/env python3
"""
Test script for the multi-monitor ROI fix
Tests the unified screenshot method
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config.config import Config
from src.core.storage.screenshot_manager import ScreenshotManager

def test_unified_roi_screenshot():
    """Test the unified ROI screenshot method"""
    print("🧪 Testing unified ROI screenshot method...")
    
    # Initialize components
    config = Config()
    config.roi = (100, 100, 400, 300)  # Test ROI
    
    screenshot_manager = ScreenshotManager(config)
    
    # Initialize screenshot manager
    if not screenshot_manager.initialize():
        print("❌ Failed to initialize screenshot manager")
        return False
    
    print(f"📐 Testing with ROI: {config.roi}")
    
    # Test full screenshot (same as preview)
    print("\n1. Testing full screenshot (preview method)...")
    full_screenshot = screenshot_manager.take_screenshot(save_to_temp=False)
    if full_screenshot:
        print(f"   ✅ Full screenshot: {len(full_screenshot)} bytes")
    else:
        print("   ❌ Full screenshot failed")
        return False
    
    # Test unified ROI screenshot (new trigger method)
    print("\n2. Testing unified ROI screenshot (new trigger method)...")
    roi_screenshot = screenshot_manager.take_unified_roi_screenshot()
    if roi_screenshot:
        print(f"   ✅ Unified ROI screenshot: {len(roi_screenshot)} bytes")
    else:
        print("   ❌ Unified ROI screenshot failed")
        return False
    
    # Test old ROI method for comparison
    print("\n3. Testing old ROI screenshot (old trigger method)...")
    old_roi_screenshot = screenshot_manager.take_roi_screenshot()
    if old_roi_screenshot:
        print(f"   ✅ Old ROI screenshot: {len(old_roi_screenshot)} bytes")
    else:
        print("   ⚠️  Old ROI screenshot failed")
    
    # Test with invalid ROI
    print("\n4. Testing with invalid ROI...")
    invalid_roi = (400, 300, 100, 100)  # right < left, bottom < top
    invalid_screenshot = screenshot_manager.take_unified_roi_screenshot(invalid_roi)
    if invalid_screenshot is None:
        print("   ✅ Invalid ROI correctly rejected")
    else:
        print("   ❌ Invalid ROI was not rejected")
        return False
    
    print("\n🎉 All tests passed! The unified ROI screenshot method is working correctly.")
    return True

if __name__ == "__main__":
    success = test_unified_roi_screenshot()
    sys.exit(0 if success else 1)
