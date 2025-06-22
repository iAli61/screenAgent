"""
Platform-specific screenshot capture implementations
Part of Phase 1.2 - Screenshot Capture Module Refactoring
"""
import os
import io
import subprocess
import base64
from typing import Optional, Tuple

from .capture_interfaces import AbstractScreenshotCapture, CaptureResult, CaptureCapabilities


class WSLPowerShellCapture(AbstractScreenshotCapture):
    """Screenshot capture using PowerShell in WSL environment"""
    
    def __init__(self, config):
        super().__init__(config)
        self._capabilities = CaptureCapabilities(
            supports_roi=True,
            supports_multi_monitor=True,
            requires_elevated=False,
            performance_rating=3
        )
        self._debug_shown = False
        self._capture_count = 0
    
    def initialize(self) -> bool:
        """Initialize WSL PowerShell capture method"""
        try:
            result = subprocess.run(
                ['powershell.exe', '-Command', 'echo "WSL PowerShell available"'],
                capture_output=True,
                timeout=10,
                text=True
            )
            
            if result.returncode == 0:
                self._initialized = True
                return True
            else:
                return False
                
        except Exception:
            return False
    
    def capture_full_screen(self) -> CaptureResult:
        """Capture full screen using PowerShell"""
        if not self._initialized:
            return CaptureResult(False, error="Not initialized")
        
        ps_script = '''
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        $Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen
        $Width = $Screen.Width
        $Height = $Screen.Height
        $Left = $Screen.Left
        $Top = $Screen.Top
        
        # Send debug info to stderr instead of stdout
        [Console]::Error.WriteLine("PowerShell Screenshot: Capturing full screen $Width x $Height at ($Left, $Top)")
        
        try {
            $bitmap = New-Object System.Drawing.Bitmap $Width, $Height
            $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphic.CopyFromScreen($Left, $Top, 0, 0, $bitmap.Size)
            
            $ms = New-Object System.IO.MemoryStream
            $bitmap.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
            $bytes = $ms.ToArray()
            $base64 = [Convert]::ToBase64String($bytes)
            
            [Console]::Error.WriteLine("PowerShell Screenshot: Successfully captured $($bytes.Length) bytes")
            
            # Only output base64 data to stdout
            Write-Output $base64
        } catch {
            [Console]::Error.WriteLine("PowerShell Screenshot Error: $($_.Exception.Message)")
            Write-Error $_.Exception.Message
            exit 1
        } finally {
            if ($graphic) { $graphic.Dispose() }
            if ($bitmap) { $bitmap.Dispose() }
            if ($ms) { $ms.Dispose() }
        }
        '''
        
        return self._execute_powershell_script(ps_script, "full screen capture")
    
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI using PowerShell with multi-monitor support"""
        if not self._initialized:
            return CaptureResult(False, error="Not initialized")
        
        if not self.validate_roi(roi):
            return CaptureResult(False, error=f"Invalid ROI coordinates: {roi}")
        
        left, top, right, bottom = roi
        width = right - left
        height = bottom - top
        
        # Debug logging for multi-monitor troubleshooting (only on first capture)
        if not self._debug_shown:
            metadata = {
                'roi': roi,
                'coordinates': {'left': left, 'top': top, 'right': right, 'bottom': bottom},
                'size': {'width': width, 'height': height}
            }
            self._debug_shown = True
        else:
            metadata = {}
        
        ps_script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        # Get virtual screen information to handle multi-monitor setups
        $Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen
        $VirtualLeft = $Screen.Left
        $VirtualTop = $Screen.Top
        $VirtualWidth = $Screen.Width
        $VirtualHeight = $Screen.Height
        
        # Get all monitors for detailed debugging - send to stderr
        $Monitors = [System.Windows.Forms.Screen]::AllScreens
        [Console]::Error.WriteLine("=== MULTI-MONITOR DEBUG ===")
        [Console]::Error.WriteLine("Virtual Screen: Left=$VirtualLeft, Top=$VirtualTop, Width=$VirtualWidth, Height=$VirtualHeight")
        [Console]::Error.WriteLine("Number of monitors: $($Monitors.Count)")
        
        for ($i = 0; $i -lt $Monitors.Count; $i++) {{
            $Monitor = $Monitors[$i]
            $Bounds = $Monitor.Bounds
            [Console]::Error.WriteLine("Monitor $($i + 1): X=$($Bounds.X), Y=$($Bounds.Y), Width=$($Bounds.Width), Height=$($Bounds.Height), Primary=$($Monitor.Primary)")
        }}
        
        # ROI coordinates (from web interface, these are screen coordinates)
        $ROILeft = {left}
        $ROITop = {top}
        $ROIWidth = {width}
        $ROIHeight = {height}
        
        [Console]::Error.WriteLine("Original ROI: Left=$ROILeft, Top=$ROITop, Width=$ROIWidth, Height=$ROIHeight")
        
        # Use ROI coordinates directly - they are already screen coordinates from the web interface
        $CaptureLeft = $ROILeft
        $CaptureTop = $ROITop
        
        [Console]::Error.WriteLine("Capture coordinates: Left=$CaptureLeft, Top=$CaptureTop, Width=$ROIWidth, Height=$ROIHeight")
        
        # Validate capture area is within virtual screen bounds
        $MaxX = $VirtualLeft + $VirtualWidth
        $MaxY = $VirtualTop + $VirtualHeight
        
        if ($CaptureLeft -lt $VirtualLeft -or $CaptureTop -lt $VirtualTop -or 
            ($CaptureLeft + $ROIWidth) -gt $MaxX -or ($CaptureTop + $ROIHeight) -gt $MaxY) {{
            [Console]::Error.WriteLine("WARNING: ROI extends beyond virtual screen bounds!")
            [Console]::Error.WriteLine("Virtual bounds: $VirtualLeft,$VirtualTop to $MaxX,$MaxY")
            [Console]::Error.WriteLine("ROI bounds: $CaptureLeft,$CaptureTop to $($CaptureLeft + $ROIWidth),$($CaptureTop + $ROIHeight)")
        }}
        
        try {{
            $bitmap = New-Object System.Drawing.Bitmap $ROIWidth, $ROIHeight
            $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
            
            [Console]::Error.WriteLine("Attempting CopyFromScreen($CaptureLeft, $CaptureTop, 0, 0, Size($ROIWidth, $ROIHeight))")
            $graphic.CopyFromScreen($CaptureLeft, $CaptureTop, 0, 0, $bitmap.Size)
            
            $ms = New-Object System.IO.MemoryStream
            $bitmap.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
            $bytes = $ms.ToArray()
            $base64 = [Convert]::ToBase64String($bytes)
            
            [Console]::Error.WriteLine("Capture successful: $($bytes.Length) bytes")
            
            # Only output base64 data to stdout
            Write-Output $base64
        }} catch {{
            [Console]::Error.WriteLine("Capture failed: $($_.Exception.Message)")
            Write-Error $_.Exception.Message
            exit 1
        }} finally {{
            if ($graphic) {{ $graphic.Dispose() }}
            if ($bitmap) {{ $bitmap.Dispose() }}
            if ($ms) {{ $ms.Dispose() }}
        }}
        '''
        
        result = self._execute_powershell_script(ps_script, f"ROI capture {roi}")
        if result.success:
            self._capture_count += 1
            result.metadata.update(metadata)
            result.metadata['capture_count'] = self._capture_count
            
        return result
    
    def _execute_powershell_script(self, script: str, operation: str) -> CaptureResult:
        """Execute a PowerShell script and return the result"""
        try:
            result = subprocess.run(
                ['powershell.exe', '-Command', script],
                capture_output=True,
                timeout=30,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                base64_data = result.stdout.strip()
                screenshot_bytes = base64.b64decode(base64_data)
                
                metadata = {
                    'method': 'wsl_powershell',
                    'operation': operation,
                    'powershell_debug': result.stderr.strip() if result.stderr.strip() else None
                }
                
                return CaptureResult(True, screenshot_bytes, metadata=metadata)
            else:
                error_msg = f"PowerShell {operation} failed: {result.stderr}"
                return CaptureResult(False, error=error_msg)
                
        except subprocess.TimeoutExpired:
            return CaptureResult(False, error=f"PowerShell {operation} timed out")
        except Exception as e:
            return CaptureResult(False, error=f"PowerShell {operation} error: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        # No persistent resources to clean up for PowerShell method
        pass


class WindowsNativeCapture(AbstractScreenshotCapture):
    """Screenshot capture using Windows native PIL ImageGrab"""
    
    def __init__(self, config):
        super().__init__(config)
        self._capabilities = CaptureCapabilities(
            supports_roi=True,
            supports_multi_monitor=True,
            requires_elevated=False,
            performance_rating=4
        )
    
    def initialize(self) -> bool:
        """Initialize Windows native capture method"""
        try:
            from PIL import ImageGrab
            test_img = ImageGrab.grab(bbox=(0, 0, 100, 100))
            if test_img:
                self._initialized = True
                return True
        except Exception:
            pass
        return False
    
    def capture_full_screen(self) -> CaptureResult:
        """Capture full screen using Windows native method"""
        if not self._initialized:
            return CaptureResult(False, error="Not initialized")
        
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            
            metadata = {
                'method': 'windows_native',
                'size': img.size,
                'mode': img.mode
            }
            
            return CaptureResult(True, img_bytes.getvalue(), metadata=metadata)
            
        except Exception as e:
            return CaptureResult(False, error=f"Windows native capture error: {e}")
    
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI using Windows native method"""
        if not self._initialized:
            return CaptureResult(False, error="Not initialized")
        
        if not self.validate_roi(roi):
            return CaptureResult(False, error=f"Invalid ROI coordinates: {roi}")
        
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab(bbox=roi)
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            
            metadata = {
                'method': 'windows_native',
                'roi': roi,
                'size': img.size,
                'mode': img.mode
            }
            
            return CaptureResult(True, img_bytes.getvalue(), metadata=metadata)
            
        except Exception as e:
            return CaptureResult(False, error=f"Windows native ROI capture error: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        # No persistent resources to clean up for PIL method
        pass


class MSSCapture(AbstractScreenshotCapture):
    """Screenshot capture using MSS (Multi-Screen Shot)"""
    
    def __init__(self, config):
        super().__init__(config)
        self._capabilities = CaptureCapabilities(
            supports_roi=True,
            supports_multi_monitor=True,
            requires_elevated=True,  # Often requires root on Linux
            performance_rating=5
        )
        self._mss_instance = None
    
    def initialize(self) -> bool:
        """Initialize MSS capture method"""
        try:
            import mss
            self._mss_instance = mss.mss()
            test_img = self._mss_instance.grab(self._mss_instance.monitors[0])
            if test_img:
                self._initialized = True
                return True
        except ImportError:
            pass
        except Exception:
            pass
        return False
    
    def capture_full_screen(self) -> CaptureResult:
        """Capture full screen using MSS"""
        if not self._initialized or not self._mss_instance:
            return CaptureResult(False, error="Not initialized")
        
        try:
            from PIL import Image
            img = self._mss_instance.grab(self._mss_instance.monitors[0])  # All monitors
            
            pil_img = Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX')
            img_bytes = io.BytesIO()
            pil_img.save(img_bytes, format='PNG')
            
            metadata = {
                'method': 'mss',
                'size': img.size,
                'monitors': len(self._mss_instance.monitors) - 1  # Exclude virtual monitor
            }
            
            return CaptureResult(True, img_bytes.getvalue(), metadata=metadata)
            
        except Exception as e:
            return CaptureResult(False, error=f"MSS capture error: {e}")
    
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI using MSS"""
        if not self._initialized or not self._mss_instance:
            return CaptureResult(False, error="Not initialized")
        
        if not self.validate_roi(roi):
            return CaptureResult(False, error=f"Invalid ROI coordinates: {roi}")
        
        try:
            from PIL import Image
            left, top, right, bottom = roi
            
            monitor = {
                'left': left,
                'top': top,
                'width': right - left,
                'height': bottom - top
            }
            img = self._mss_instance.grab(monitor)
            
            pil_img = Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX')
            img_bytes = io.BytesIO()
            pil_img.save(img_bytes, format='PNG')
            
            metadata = {
                'method': 'mss',
                'roi': roi,
                'size': img.size
            }
            
            return CaptureResult(True, img_bytes.getvalue(), metadata=metadata)
            
        except Exception as e:
            return CaptureResult(False, error=f"MSS ROI capture error: {e}")
    
    def cleanup(self) -> None:
        """Clean up MSS resources"""
        if self._mss_instance:
            self._mss_instance.close()
            self._mss_instance = None


class PyAutoGUICapture(AbstractScreenshotCapture):
    """Screenshot capture using PyAutoGUI"""
    
    def __init__(self, config):
        super().__init__(config)
        self._capabilities = CaptureCapabilities(
            supports_roi=True,
            supports_multi_monitor=False,  # Limited multi-monitor support
            requires_elevated=False,
            performance_rating=2
        )
    
    def initialize(self) -> bool:
        """Initialize PyAutoGUI capture method"""
        try:
            import pyautogui
            pyautogui.FAILSAFE = False  # Disable fail-safe for automation
            test_img = pyautogui.screenshot(region=(0, 0, 100, 100))
            if test_img:
                self._initialized = True
                return True
        except ImportError:
            pass
        except Exception:
            pass
        return False
    
    def capture_full_screen(self) -> CaptureResult:
        """Capture full screen using PyAutoGUI"""
        if not self._initialized:
            return CaptureResult(False, error="Not initialized")
        
        try:
            import pyautogui
            img = pyautogui.screenshot()
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            
            metadata = {
                'method': 'pyautogui',
                'size': img.size,
                'mode': img.mode
            }
            
            return CaptureResult(True, img_bytes.getvalue(), metadata=metadata)
            
        except Exception as e:
            return CaptureResult(False, error=f"PyAutoGUI capture error: {e}")
    
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI using PyAutoGUI"""
        if not self._initialized:
            return CaptureResult(False, error="Not initialized")
        
        if not self.validate_roi(roi):
            return CaptureResult(False, error=f"Invalid ROI coordinates: {roi}")
        
        try:
            import pyautogui
            left, top, right, bottom = roi
            width = right - left
            height = bottom - top
            
            img = pyautogui.screenshot(region=(left, top, width, height))
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            
            metadata = {
                'method': 'pyautogui',
                'roi': roi,
                'size': img.size,
                'mode': img.mode
            }
            
            return CaptureResult(True, img_bytes.getvalue(), metadata=metadata)
            
        except Exception as e:
            return CaptureResult(False, error=f"PyAutoGUI ROI capture error: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        # No persistent resources to clean up for PyAutoGUI
        pass


class HeadlessCapture(AbstractScreenshotCapture):
    """Dummy capture for headless environments"""
    
    def __init__(self, config):
        super().__init__(config)
        self._capabilities = CaptureCapabilities(
            supports_roi=False,
            supports_multi_monitor=False,
            requires_elevated=False,
            performance_rating=0
        )
    
    def initialize(self) -> bool:
        """Initialize headless capture (no-op)"""
        self._initialized = True
        return True
    
    def capture_full_screen(self) -> CaptureResult:
        """Capture full screen (returns empty result)"""
        return CaptureResult(False, error="Headless environment - no display available")
    
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI (returns empty result)"""
        return CaptureResult(False, error="Headless environment - no display available")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        pass
