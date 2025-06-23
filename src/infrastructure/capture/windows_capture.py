"""
Windows-specific screenshot capture implementation
Uses native Windows APIs for optimal performance
"""
import os
import io
import subprocess
import base64
from typing import Tuple, Dict, Any, Optional

from . import ICaptureHandler, CaptureResult, CaptureMethod, CaptureCapabilities


class WindowsNativeCapture(ICaptureHandler):
    """Windows native screenshot capture using PowerShell"""
    
    def __init__(self):
        super().__init__()
        self._capabilities = CaptureCapabilities(
            method=CaptureMethod.WINDOWS_NATIVE,
            supports_roi=True,
            supports_multi_monitor=True,
            requires_elevated=False,
            performance_rating=4,
            reliability_rating=5,
            platform_specific=True
        )
    
    def can_handle(self) -> bool:
        """Check if Windows native capture is available"""
        return os.name == 'nt' or self._is_wsl_with_powershell()
    
    def _is_wsl_with_powershell(self) -> bool:
        """Check if running in WSL with PowerShell access"""
        try:
            # Check for WSL environment variable
            if 'WSL_DISTRO_NAME' in os.environ:
                # Test PowerShell availability
                result = subprocess.run(
                    ['powershell.exe', '-Command', 'echo "test"'],
                    capture_output=True,
                    timeout=5,
                    text=True
                )
                return result.returncode == 0
        except Exception:
            pass
        return False
    
    def initialize(self) -> bool:
        """Initialize Windows native capture"""
        try:
            # Test PowerShell availability and required assemblies
            test_script = '''
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            Write-Output "OK"
            '''
            
            result = subprocess.run(
                ['powershell.exe', '-Command', test_script],
                capture_output=True,
                timeout=10,
                text=True
            )
            
            if result.returncode == 0 and "OK" in result.stdout:
                self._initialized = True
                return True
            
            return False
            
        except Exception as e:
            print(f"Windows native capture initialization failed: {e}")
            return False
    
    def _capture_full_screen(self) -> CaptureResult:
        """Capture full screen using PowerShell"""
        ps_script = '''
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        try {
            $Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen
            $Width = $Screen.Width
            $Height = $Screen.Height
            $Left = $Screen.Left
            $Top = $Screen.Top
            
            $bitmap = New-Object System.Drawing.Bitmap $Width, $Height
            $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphic.CopyFromScreen($Left, $Top, 0, 0, $bitmap.Size)
            
            $ms = New-Object System.IO.MemoryStream
            $bitmap.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
            $bytes = $ms.ToArray()
            $base64 = [Convert]::ToBase64String($bytes)
            
            Write-Output $base64
        } catch {
            Write-Error $_.Exception.Message
            exit 1
        } finally {
            if ($graphic) { $graphic.Dispose() }
            if ($bitmap) { $bitmap.Dispose() }
            if ($ms) { $ms.Dispose() }
        }
        '''
        
        return self._execute_powershell_script(ps_script, "full screen capture")
    
    def _capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture region of interest using PowerShell"""
        left, top, right, bottom = roi
        width = right - left
        height = bottom - top
        
        ps_script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        try {{
            $bitmap = New-Object System.Drawing.Bitmap {width}, {height}
            $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphic.CopyFromScreen({left}, {top}, 0, 0, $bitmap.Size)
            
            $ms = New-Object System.IO.MemoryStream
            $bitmap.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
            $bytes = $ms.ToArray()
            $base64 = [Convert]::ToBase64String($bytes)
            
            Write-Output $base64
        }} catch {{
            Write-Error $_.Exception.Message
            exit 1
        }} finally {{
            if ($graphic) {{ $graphic.Dispose() }}
            if ($bitmap) {{ $bitmap.Dispose() }}
            if ($ms) {{ $ms.Dispose() }}
        }}
        '''
        
        return self._execute_powershell_script(ps_script, f"ROI capture {roi}")
    
    def _execute_powershell_script(self, script: str, operation: str) -> CaptureResult:
        """Execute PowerShell script and return capture result"""
        try:
            result = subprocess.run(
                ['powershell.exe', '-Command', script],
                capture_output=True,
                timeout=30,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # Decode base64 data
                base64_data = result.stdout.strip()
                image_data = base64.b64decode(base64_data)
                
                metadata = {
                    'method': 'windows_native',
                    'operation': operation,
                    'size': len(image_data)
                }
                
                return CaptureResult(True, image_data, metadata=metadata)
            else:
                error_msg = result.stderr if result.stderr else "PowerShell script failed"
                return CaptureResult(False, error=f"Windows native {operation} failed: {error_msg}")
                
        except subprocess.TimeoutExpired:
            return CaptureResult(False, error=f"Windows native {operation} timed out")
        except Exception as e:
            return CaptureResult(False, error=f"Windows native {operation} error: {str(e)}")
    
    # Add compatibility methods for direct access from CaptureServiceImpl
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Direct capture ROI method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="Windows native capture not initialized")
        return self._capture_roi(roi)
    
    def capture_full_screen(self) -> CaptureResult:
        """Direct capture full screen method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="Windows native capture not initialized")
        return self._capture_full_screen()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self._initialized = False


class WindowsMSSCapture(ICaptureHandler):
    """Windows screenshot capture using MSS library"""
    
    def __init__(self):
        super().__init__()
        self._capabilities = CaptureCapabilities(
            method=CaptureMethod.MSS,
            supports_roi=True,
            supports_multi_monitor=True,
            requires_elevated=False,
            performance_rating=3,
            reliability_rating=4,
            platform_specific=False
        )
        self._mss = None
    
    def can_handle(self) -> bool:
        """Check if MSS library is available"""
        try:
            import mss
            return True
        except ImportError:
            return False
    
    def initialize(self) -> bool:
        """Initialize MSS capture"""
        try:
            import mss
            self._mss = mss.mss()
            self._initialized = True
            return True
        except Exception as e:
            print(f"MSS capture initialization failed: {e}")
            return False
    
    def _capture_full_screen(self) -> CaptureResult:
        """Capture full screen using MSS"""
        try:
            # Get the first monitor (usually primary)
            monitor = self._mss.monitors[0]  # Monitor 0 is all monitors combined
            
            # Capture screenshot
            screenshot = self._mss.grab(monitor)
            
            # Convert to PNG bytes
            png_data = self._mss.tools.to_png(screenshot.rgb, screenshot.size)
            
            metadata = {
                'method': 'mss',
                'operation': 'full_screen',
                'monitor': monitor,
                'size': len(png_data)
            }
            
            return CaptureResult(True, png_data, metadata=metadata)
            
        except Exception as e:
            return CaptureResult(False, error=f"MSS full screen capture failed: {str(e)}")
    
    def _capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI using MSS"""
        try:
            left, top, right, bottom = roi
            
            # MSS expects different format
            monitor_region = {
                'left': left,
                'top': top,
                'width': right - left,
                'height': bottom - top
            }
            
            # Capture screenshot
            screenshot = self._mss.grab(monitor_region)
            
            # Convert to PNG bytes
            png_data = self._mss.tools.to_png(screenshot.rgb, screenshot.size)
            
            metadata = {
                'method': 'mss',
                'operation': 'roi_capture',
                'roi': roi,
                'size': len(png_data)
            }
            
            return CaptureResult(True, png_data, metadata=metadata)
            
        except Exception as e:
            return CaptureResult(False, error=f"MSS ROI capture failed: {str(e)}")
    
    # Add compatibility methods for direct access from CaptureServiceImpl
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Direct capture ROI method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="MSS capture not initialized")
        return self._capture_roi(roi)
    
    def capture_full_screen(self) -> CaptureResult:
        """Direct capture full screen method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="MSS capture not initialized")
        return self._capture_full_screen()
    
    def cleanup(self) -> None:
        """Clean up MSS resources"""
        if self._mss:
            self._mss.close()
            self._mss = None
        self._initialized = False
