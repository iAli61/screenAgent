#!/usr/bin/env python3
"""Debug platform detection"""
import os
import sys
import platform

# Add src to path
sys.path.append('src')

print("=== Basic Platform Info ===")
print(f"Platform: {platform.system()}")
print(f"OS Name: {os.name}")
print(f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
print(f"WSL_DISTRO_NAME: {os.environ.get('WSL_DISTRO_NAME', 'Not set')}")

# Check /proc/version for WSL
try:
    with open('/proc/version', 'r') as f:
        content = f.read().lower()
        is_wsl = 'microsoft' in content or 'wsl' in content
        print(f"WSL in /proc/version: {is_wsl}")
        print(f"Proc version (first 100 chars): {content[:100]}")
except Exception as e:
    print(f"Could not read /proc/version: {e}")

# Test PowerShell
import subprocess
try:
    result = subprocess.run(['powershell.exe', '-Command', 'echo test'], 
                          capture_output=True, timeout=5, text=True)
    print(f"PowerShell available: {result.returncode == 0}")
    if result.returncode == 0:
        print(f"PowerShell output: {result.stdout.strip()}")
except Exception as e:
    print(f"PowerShell test failed: {e}")

print("\n=== Clean Architecture Platform Detection ===")
try:
    from src.infrastructure.capture.platform_detector import PlatformDetector
    
    detector = PlatformDetector()
    print(f"Is Windows: {detector.is_windows()}")
    print(f"Is Linux: {detector.is_linux()}")
    print(f"Is WSL: {detector.is_wsl()}")
    print(f"Has X11: {detector.has_x11()}")
    print(f"Has PowerShell: {detector.has_powershell()}")
    
    methods = detector.get_recommended_methods()
    print(f"Recommended methods: {[m.value for m in methods]}")
    
    print("\nDisplay info:")
    for k, v in detector.get_display_info().items():
        print(f"  {k}: {v}")
        
except Exception as e:
    print(f"Error with clean architecture detection: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Legacy Platform Detection ===")
try:
    from src.utils.platform_detection import is_wsl, is_windows, is_linux_with_display, get_platform_info
    
    print(f"Legacy is_wsl: {is_wsl()}")
    print(f"Legacy is_windows: {is_windows()}")
    print(f"Legacy is_linux_with_display: {is_linux_with_display()}")
    
    print("Legacy platform info:")
    for k, v in get_platform_info().items():
        print(f"  {k}: {v}")
        
except Exception as e:
    print(f"Error with legacy detection: {e}")
    import traceback
    traceback.print_exc()
