"""
Platform detection for ScreenAgent
Detects WSL, Linux, Windows environments and chooses appropriate screenshot methods
"""
import os
import platform
import subprocess
from typing import Optional

def is_wsl() -> bool:
    """Check if running in Windows Subsystem for Linux"""
    try:
        # Check for WSL in kernel version
        with open('/proc/version', 'r') as f:
            version = f.read().lower()
            if 'microsoft' in version or 'wsl' in version:
                return True
        
        # Alternative check: WSL environment variable
        if os.environ.get('WSL_DISTRO_NAME'):
            return True
            
        # Check if we can run PowerShell (another WSL indicator)
        try:
            result = subprocess.run(
                ['powershell.exe', '-Command', 'echo "test"'], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
            
    except Exception:
        pass
    
    return False

def is_linux_with_display() -> bool:
    """Check if running on Linux with a display server"""
    if platform.system() != 'Linux':
        return False
    
    if is_wsl():
        return False
    
    # Check for display environment variables
    return bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'))

def is_windows() -> bool:
    """Check if running on native Windows"""
    return platform.system() == 'Windows'

def get_platform_info() -> dict:
    """Get comprehensive platform information"""
    return {
        'system': platform.system(),
        'machine': platform.machine(),
        'platform': platform.platform(),
        'is_wsl': is_wsl(),
        'is_linux_with_display': is_linux_with_display(),
        'is_windows': is_windows(),
        'has_display': bool(os.environ.get('DISPLAY')),
        'has_wayland': bool(os.environ.get('WAYLAND_DISPLAY')),
        'python_version': platform.python_version(),
    }

def get_recommended_screenshot_method() -> str:
    """Get the recommended screenshot method for the current platform"""
    if is_wsl():
        return 'wsl_powershell'
    elif is_windows():
        return 'windows_native'
    elif is_linux_with_display():
        if os.geteuid() == 0:  # Running as root
            return 'mss'
        else:
            return 'pyautogui'
    else:
        return 'headless'  # No display available

# Legacy compatibility
WSL_MODE = is_wsl()

if __name__ == "__main__":
    # Print platform information when run directly
    info = get_platform_info()
    print("Platform Information:")
    print("=" * 30)
    for key, value in info.items():
        print(f"{key}: {value}")
    
    print(f"\nRecommended screenshot method: {get_recommended_screenshot_method()}")
