#!/usr/bin/env python3
"""
Simple test to verify the refactored screenshot capture module works
"""
import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("Testing refactored screenshot capture...")

try:
    from src.core.config import Config
    print("✅ Config import successful")
except ImportError as e:
    print(f"❌ Config import failed: {e}")

try:
    from src.core.capture_interfaces import CaptureMethod, ScreenshotCaptureFactory
    print("✅ Capture interfaces import successful")
except ImportError as e:
    print(f"❌ Capture interfaces import failed: {e}")

try:
    from src.core.capture_implementations import WSLPowerShellCapture
    print("✅ Capture implementations import successful")
except ImportError as e:
    print(f"❌ Capture implementations import failed: {e}")

try:
    from src.core.capture.screenshot_capture import ScreenshotCaptureManager
    print("✅ Screenshot capture manager import successful")
except ImportError as e:
    print(f"❌ Screenshot capture manager import failed: {e}")

print("Basic import test completed.")
