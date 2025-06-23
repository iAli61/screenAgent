"""
Platform detection utility for capture system
Detects the current platform and available capture methods
"""
import os
import platform
import subprocess
import shutil
from typing import Dict, Any, List

from . import IPlatformDetector, CaptureMethod


class PlatformDetector(IPlatformDetector):
    """Platform detection implementation"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def is_windows(self) -> bool:
        """Check if running on Windows"""
        if 'is_windows' not in self._cache:
            self._cache['is_windows'] = os.name == 'nt' or platform.system() == 'Windows'
        return self._cache['is_windows']
    
    def is_linux(self) -> bool:
        """Check if running on Linux"""
        if 'is_linux' not in self._cache:
            self._cache['is_linux'] = os.name == 'posix' and platform.system() == 'Linux'
        return self._cache['is_linux']
    
    def is_wsl(self) -> bool:
        """Check if running in WSL"""
        if 'is_wsl' not in self._cache:
            # Check for WSL environment variable
            wsl_env = 'WSL_DISTRO_NAME' in os.environ
            
            # Also check /proc/version for WSL signature
            wsl_proc = False
            try:
                with open('/proc/version', 'r') as f:
                    content = f.read().lower()
                    wsl_proc = 'microsoft' in content or 'wsl' in content
            except Exception:
                pass
            
            self._cache['is_wsl'] = wsl_env or wsl_proc
        return self._cache['is_wsl']
    
    def is_wayland(self) -> bool:
        """Check if running on Wayland"""
        if 'is_wayland' not in self._cache:
            self._cache['is_wayland'] = 'WAYLAND_DISPLAY' in os.environ
        return self._cache['is_wayland']
    
    def has_x11(self) -> bool:
        """Check if X11 is available"""
        if 'has_x11' not in self._cache:
            self._cache['has_x11'] = 'DISPLAY' in os.environ
        return self._cache['has_x11']
    
    def has_powershell(self) -> bool:
        """Check if PowerShell is available"""
        if 'has_powershell' not in self._cache:
            try:
                result = subprocess.run(
                    ['powershell.exe', '-Command', 'echo "test"'],
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                self._cache['has_powershell'] = result.returncode == 0
            except Exception:
                self._cache['has_powershell'] = False
        return self._cache['has_powershell']
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get display information"""
        info = {
            'platform': platform.system(),
            'os_name': os.name,
            'is_windows': self.is_windows(),
            'is_linux': self.is_linux(),
            'is_wsl': self.is_wsl(),
            'is_wayland': self.is_wayland(),
            'has_x11': self.has_x11(),
            'has_powershell': self.has_powershell(),
            'environment_vars': {},
            'available_tools': []
        }
        
        # Capture relevant environment variables
        env_vars = ['DISPLAY', 'WAYLAND_DISPLAY', 'WSL_DISTRO_NAME', 'XDG_SESSION_TYPE']
        for var in env_vars:
            if var in os.environ:
                info['environment_vars'][var] = os.environ[var]
        
        # Check for available capture tools
        tools = ['scrot', 'import', 'grim', 'gnome-screenshot', 'powershell.exe']
        for tool in tools:
            if shutil.which(tool):
                info['available_tools'].append(tool)
        
        # Check for Python libraries
        python_libs = ['mss', 'pyautogui', 'PIL', 'pyscreenshot']
        for lib in python_libs:
            try:
                __import__(lib)
                info['available_tools'].append(f'python:{lib}')
            except ImportError:
                pass
        
        return info
    
    def get_recommended_methods(self) -> List[CaptureMethod]:
        """Get recommended capture methods for current platform in priority order"""
        methods = []
        
        # WSL check must come first to avoid incorrect detection
        if self.is_wsl():
            # WSL environment - PowerShell bridge is best
            if self.has_powershell():
                methods.append(CaptureMethod.WSL_POWERSHELL)
            methods.append(CaptureMethod.PYAUTOGUI)  # Fallback
            # Never add X11 or Wayland methods for WSL even if DISPLAY is set
            
        elif self.is_windows():
            # Native Windows environment
            methods.append(CaptureMethod.WINDOWS_NATIVE)
            methods.append(CaptureMethod.MSS)
            methods.append(CaptureMethod.PYAUTOGUI)
            
        elif self.is_linux():
            if self.is_wayland():
                # Wayland environment
                methods.append(CaptureMethod.LINUX_WAYLAND)
                methods.append(CaptureMethod.MSS)
                methods.append(CaptureMethod.PYAUTOGUI)
            elif self.has_x11():
                # X11 environment
                methods.append(CaptureMethod.LINUX_X11)
                methods.append(CaptureMethod.MSS)
                methods.append(CaptureMethod.PYAUTOGUI)
            else:
                # Headless or unknown environment
                methods.append(CaptureMethod.MSS)
                methods.append(CaptureMethod.PYAUTOGUI)
        
        return methods
    
    def clear_cache(self) -> None:
        """Clear cached detection results"""
        self._cache.clear()
