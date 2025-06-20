#!/usr/bin/env python3
"""Test script to check imports"""
import sys
import os
import traceback

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.append('src')

print("Testing imports...")

try:
    from src.core.config.config import Config
    print("✓ Config import successful")
except Exception as e:
    print(f"✗ Config import failed: {e}")
    traceback.print_exc()

try:
    from src.utils.platform_detection import get_recommended_screenshot_method
    print("✓ Platform detection import successful")
except Exception as e:
    print(f"✗ Platform detection import failed: {e}")
    traceback.print_exc()

try:
    from src.core.capture.screenshot_capture import ScreenshotCapture
    print("✓ ScreenshotCapture import successful")
except Exception as e:
    print(f"✗ ScreenshotCapture import failed: {e}")
    traceback.print_exc()

try:
    from src.core.monitoring.roi_monitor import ROIMonitor
    print("✓ ROIMonitor import successful")
except Exception as e:
    print(f"✗ ROIMonitor import failed: {e}")
    traceback.print_exc()

try:
    from src.core.storage.screenshot_manager import ScreenshotManager
    print("✓ ScreenshotManager import successful")
except Exception as e:
    print(f"✗ ScreenshotManager import failed: {e}")
    traceback.print_exc()

try:
    from src.utils.keyboard_handler import KeyboardHandler
    print("✓ KeyboardHandler import successful")
except Exception as e:
    print(f"✗ KeyboardHandler import failed: {e}")
    traceback.print_exc()

try:
    from src.api.server import ScreenAgentServer
    print("✓ ScreenAgentServer import successful")
except Exception as e:
    print(f"✗ ScreenAgentServer import failed: {e}")
    traceback.print_exc()

print("Import testing complete.")
