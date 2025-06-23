"""
Linux-specific screenshot capture implementation
Supports both X11 and Wayland environments
"""
import os
import io
import subprocess
import shutil
from typing import Tuple, Dict, Any, Optional

from . import ICaptureHandler, CaptureResult, CaptureMethod, CaptureCapabilities


class LinuxX11Capture(ICaptureHandler):
    """Linux X11 screenshot capture using imagemagick/scrot"""
    
    def __init__(self):
        super().__init__()
        self._capabilities = CaptureCapabilities(
            method=CaptureMethod.LINUX_X11,
            supports_roi=True,
            supports_multi_monitor=True,
            requires_elevated=False,
            performance_rating=4,
            reliability_rating=4,
            platform_specific=True
        )
        self._capture_tool = None
    
    def can_handle(self) -> bool:
        """Check if X11 capture is available"""
        # Exclude WSL environments
        if 'WSL_DISTRO_NAME' in os.environ:
            return False
            
        try:
            # Also check /proc/version for WSL signature
            with open('/proc/version', 'r') as f:
                content = f.read().lower()
                if 'microsoft' in content or 'wsl' in content:
                    return False
        except Exception:
            pass
            
        # Check if running on Linux with X11
        if os.name != 'posix':
            return False
        
        # Check for X11 environment
        if 'DISPLAY' not in os.environ:
            return False
        
        # Check for available tools
        for tool in ['scrot', 'import', 'gnome-screenshot']:
            if shutil.which(tool):
                return True
        
        return False
    
    def initialize(self) -> bool:
        """Initialize X11 capture"""
        try:
            # Find best available capture tool
            tools = [
                ('scrot', self._test_scrot),
                ('import', self._test_imagemagick),
                ('gnome-screenshot', self._test_gnome_screenshot)
            ]
            
            for tool_name, test_func in tools:
                if shutil.which(tool_name) and test_func():
                    self._capture_tool = tool_name
                    self._initialized = True
                    return True
            
            return False
            
        except Exception as e:
            print(f"X11 capture initialization failed: {e}")
            return False
    
    def _test_scrot(self) -> bool:
        """Test scrot availability"""
        try:
            result = subprocess.run(['scrot', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _test_imagemagick(self) -> bool:
        """Test ImageMagick import availability"""
        try:
            result = subprocess.run(['import', '-version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _test_gnome_screenshot(self) -> bool:
        """Test GNOME screenshot tool availability"""
        try:
            result = subprocess.run(['gnome-screenshot', '--version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _capture_full_screen(self) -> CaptureResult:
        """Capture full screen using available X11 tool"""
        if self._capture_tool == 'scrot':
            return self._scrot_full_screen()
        elif self._capture_tool == 'import':
            return self._imagemagick_full_screen()
        elif self._capture_tool == 'gnome-screenshot':
            return self._gnome_full_screen()
        else:
            return CaptureResult(False, error="No X11 capture tool available")
    
    def _capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI using available X11 tool"""
        if self._capture_tool == 'scrot':
            return self._scrot_roi(roi)
        elif self._capture_tool == 'import':
            return self._imagemagick_roi(roi)
        elif self._capture_tool == 'gnome-screenshot':
            return self._gnome_roi(roi)
        else:
            return CaptureResult(False, error="No X11 ROI capture tool available")
    
    def _scrot_full_screen(self) -> CaptureResult:
        """Capture full screen using scrot"""
        try:
            result = subprocess.run(
                ['scrot', '-z', '-'],  # -z for compression, - for stdout
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                metadata = {
                    'method': 'scrot',
                    'operation': 'full_screen',
                    'tool': 'scrot',
                    'size': len(result.stdout)
                }
                return CaptureResult(True, result.stdout, metadata=metadata)
            else:
                error_msg = result.stderr.decode() if result.stderr else "scrot failed"
                return CaptureResult(False, error=f"scrot full screen failed: {error_msg}")
                
        except Exception as e:
            return CaptureResult(False, error=f"scrot full screen error: {str(e)}")
    
    def _scrot_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI using scrot"""
        try:
            left, top, right, bottom = roi
            width = right - left
            height = bottom - top
            
            # scrot format: -a x,y,w,h
            result = subprocess.run(
                ['scrot', '-a', f'{left},{top},{width},{height}', '-z', '-'],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                metadata = {
                    'method': 'scrot',
                    'operation': 'roi_capture',
                    'roi': roi,
                    'tool': 'scrot',
                    'size': len(result.stdout)
                }
                return CaptureResult(True, result.stdout, metadata=metadata)
            else:
                error_msg = result.stderr.decode() if result.stderr else "scrot ROI failed"
                return CaptureResult(False, error=f"scrot ROI capture failed: {error_msg}")
                
        except Exception as e:
            return CaptureResult(False, error=f"scrot ROI capture error: {str(e)}")
    
    def _imagemagick_full_screen(self) -> CaptureResult:
        """Capture full screen using ImageMagick import"""
        try:
            result = subprocess.run(
                ['import', '-window', 'root', 'png:-'],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                metadata = {
                    'method': 'imagemagick',
                    'operation': 'full_screen',
                    'tool': 'import',
                    'size': len(result.stdout)
                }
                return CaptureResult(True, result.stdout, metadata=metadata)
            else:
                error_msg = result.stderr.decode() if result.stderr else "import failed"
                return CaptureResult(False, error=f"ImageMagick full screen failed: {error_msg}")
                
        except Exception as e:
            return CaptureResult(False, error=f"ImageMagick full screen error: {str(e)}")
    
    def _imagemagick_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI using ImageMagick import"""
        try:
            left, top, right, bottom = roi
            width = right - left
            height = bottom - top
            
            # ImageMagick crop format: widthxheight+x+y
            crop_spec = f'{width}x{height}+{left}+{top}'
            
            result = subprocess.run(
                ['import', '-window', 'root', '-crop', crop_spec, 'png:-'],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                metadata = {
                    'method': 'imagemagick',
                    'operation': 'roi_capture',
                    'roi': roi,
                    'tool': 'import',
                    'size': len(result.stdout)
                }
                return CaptureResult(True, result.stdout, metadata=metadata)
            else:
                error_msg = result.stderr.decode() if result.stderr else "import ROI failed"
                return CaptureResult(False, error=f"ImageMagick ROI capture failed: {error_msg}")
                
        except Exception as e:
            return CaptureResult(False, error=f"ImageMagick ROI capture error: {str(e)}")
    
    def _gnome_full_screen(self) -> CaptureResult:
        """Capture full screen using GNOME screenshot"""
        try:
            result = subprocess.run(
                ['gnome-screenshot', '-f', '/dev/stdout'],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                metadata = {
                    'method': 'gnome_screenshot',
                    'operation': 'full_screen',
                    'tool': 'gnome-screenshot',
                    'size': len(result.stdout)
                }
                return CaptureResult(True, result.stdout, metadata=metadata)
            else:
                error_msg = result.stderr.decode() if result.stderr else "gnome-screenshot failed"
                return CaptureResult(False, error=f"GNOME screenshot full screen failed: {error_msg}")
                
        except Exception as e:
            return CaptureResult(False, error=f"GNOME screenshot full screen error: {str(e)}")
    
    def _gnome_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """GNOME screenshot doesn't support ROI directly, fallback to full screen"""
        # GNOME screenshot doesn't have built-in ROI support
        # We could capture full screen and crop, but that's inefficient
        return CaptureResult(False, error="GNOME screenshot doesn't support ROI capture")
    
    # Add compatibility methods for direct access from CaptureServiceImpl
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Direct capture ROI method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="Linux X11 capture not initialized")
        return self._capture_roi(roi)
    
    def capture_full_screen(self) -> CaptureResult:
        """Direct capture full screen method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="Linux X11 capture not initialized")
        return self._capture_full_screen()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self._capture_tool = None
        self._initialized = False


class LinuxWaylandCapture(ICaptureHandler):
    """Linux Wayland screenshot capture using grim/wlroots tools"""
    
    def __init__(self):
        super().__init__()
        self._capabilities = CaptureCapabilities(
            method=CaptureMethod.LINUX_WAYLAND,
            supports_roi=True,
            supports_multi_monitor=True,
            requires_elevated=False,
            performance_rating=3,
            reliability_rating=3,
            platform_specific=True
        )
        self._capture_tool = None
    
    def can_handle(self) -> bool:
        """Check if Wayland capture is available"""
        # Exclude WSL environments
        if 'WSL_DISTRO_NAME' in os.environ:
            return False
            
        try:
            # Also check /proc/version for WSL signature
            with open('/proc/version', 'r') as f:
                content = f.read().lower()
                if 'microsoft' in content or 'wsl' in content:
                    return False
        except Exception:
            pass
            
        # Check if running on Linux with Wayland
        if os.name != 'posix':
            return False
        
        # Check for Wayland environment
        if 'WAYLAND_DISPLAY' not in os.environ:
            return False
        
        # Check for available tools
        for tool in ['grim', 'grimshot']:
            if shutil.which(tool):
                return True
        
        return False
    
    def initialize(self) -> bool:
        """Initialize Wayland capture"""
        try:
            # Find best available capture tool
            if shutil.which('grim'):
                self._capture_tool = 'grim'
                self._initialized = True
                return True
            elif shutil.which('grimshot'):
                self._capture_tool = 'grimshot'
                self._initialized = True
                return True
            
            return False
            
        except Exception as e:
            print(f"Wayland capture initialization failed: {e}")
            return False
    
    def _capture_full_screen(self) -> CaptureResult:
        """Capture full screen using Wayland tools"""
        if self._capture_tool == 'grim':
            return self._grim_full_screen()
        elif self._capture_tool == 'grimshot':
            return self._grimshot_full_screen()
        else:
            return CaptureResult(False, error="No Wayland capture tool available")
    
    def _capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI using Wayland tools"""
        if self._capture_tool == 'grim':
            return self._grim_roi(roi)
        elif self._capture_tool == 'grimshot':
            return self._grimshot_roi(roi)
        else:
            return CaptureResult(False, error="No Wayland ROI capture tool available")
    
    def _grim_full_screen(self) -> CaptureResult:
        """Capture full screen using grim"""
        try:
            result = subprocess.run(
                ['grim', '-'],  # - for stdout
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                metadata = {
                    'method': 'grim',
                    'operation': 'full_screen',
                    'tool': 'grim',
                    'size': len(result.stdout)
                }
                return CaptureResult(True, result.stdout, metadata=metadata)
            else:
                error_msg = result.stderr.decode() if result.stderr else "grim failed"
                return CaptureResult(False, error=f"grim full screen failed: {error_msg}")
                
        except Exception as e:
            return CaptureResult(False, error=f"grim full screen error: {str(e)}")
    
    def _grim_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI using grim"""
        try:
            left, top, right, bottom = roi
            width = right - left
            height = bottom - top
            
            # grim geometry format: "x,y width,height"
            geometry = f"{left},{top} {width}x{height}"
            
            result = subprocess.run(
                ['grim', '-g', geometry, '-'],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                metadata = {
                    'method': 'grim',
                    'operation': 'roi_capture',
                    'roi': roi,
                    'tool': 'grim',
                    'size': len(result.stdout)
                }
                return CaptureResult(True, result.stdout, metadata=metadata)
            else:
                error_msg = result.stderr.decode() if result.stderr else "grim ROI failed"
                return CaptureResult(False, error=f"grim ROI capture failed: {error_msg}")
                
        except Exception as e:
            return CaptureResult(False, error=f"grim ROI capture error: {str(e)}")
    
    def _grimshot_full_screen(self) -> CaptureResult:
        """Capture full screen using grimshot"""
        try:
            result = subprocess.run(
                ['grimshot', 'save', 'screen', '-'],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                metadata = {
                    'method': 'grimshot',
                    'operation': 'full_screen',
                    'tool': 'grimshot',
                    'size': len(result.stdout)
                }
                return CaptureResult(True, result.stdout, metadata=metadata)
            else:
                error_msg = result.stderr.decode() if result.stderr else "grimshot failed"
                return CaptureResult(False, error=f"grimshot full screen failed: {error_msg}")
                
        except Exception as e:
            return CaptureResult(False, error=f"grimshot full screen error: {str(e)}")
    
    def _grimshot_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """grimshot doesn't support direct ROI, use area selection"""
        # grimshot has area selection but not direct coordinates
        return CaptureResult(False, error="grimshot doesn't support direct ROI coordinates")
    
    # Add compatibility methods for direct access from CaptureServiceImpl
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Direct capture ROI method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="Linux Wayland capture not initialized")
        return self._capture_roi(roi)
    
    def capture_full_screen(self) -> CaptureResult:
        """Direct capture full screen method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="Linux Wayland capture not initialized")
        return self._capture_full_screen()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self._capture_tool = None
        self._initialized = False
