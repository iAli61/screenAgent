"""
Cross-platform screenshot capture for ScreenAgent
Handles WSL, Windows, Linux with appropriate methods
"""
import os
import io
import subprocess
import base64
from typing import Optional, Tuple
from PIL import Image

from ...utils.platform_detection import get_recommended_screenshot_method
from ..config.config import Config


class ScreenshotCapture:
    """Cross-platform screenshot capture with multi-monitor support"""
    
    def __init__(self, config: Config):
        self.config = config
        self.method = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize the appropriate screenshot method"""
        self.method = get_recommended_screenshot_method()
        
        try:
            if self.method == 'wsl_powershell':
                return self._init_wsl_powershell()
            elif self.method == 'windows_native':
                return self._init_windows_native()
            elif self.method == 'mss':
                return self._init_mss()
            elif self.method == 'pyautogui':
                return self._init_pyautogui()
            else:
                print(f"⚠️  No suitable screenshot method available for this environment")
                return False
                
        except Exception as e:
            print(f"❌ Failed to initialize screenshot method {self.method}: {e}")
            return False
    
    def _init_wsl_powershell(self) -> bool:
        """Initialize WSL PowerShell screenshot method"""
        try:
            result = subprocess.run(
                ['powershell.exe', '-Command', 'echo "WSL PowerShell available"'],
                capture_output=True,
                timeout=10,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ WSL PowerShell screenshot method initialized")
                self._initialized = True
                return True
            else:
                print(f"❌ PowerShell test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ WSL PowerShell initialization failed: {e}")
            return False
    
    def _init_windows_native(self) -> bool:
        """Initialize Windows native screenshot method"""
        try:
            from PIL import ImageGrab
            test_img = ImageGrab.grab(bbox=(0, 0, 100, 100))
            if test_img:
                print("✅ Windows native screenshot method initialized")
                self._initialized = True
                return True
        except Exception as e:
            print(f"❌ Windows native initialization failed: {e}")
        return False
    
    def _init_mss(self) -> bool:
        """Initialize MSS screenshot method"""
        try:
            import mss
            with mss.mss() as sct:
                test_img = sct.grab(sct.monitors[0])
                if test_img:
                    print("✅ MSS screenshot method initialized")
                    self._initialized = True
                    return True
        except ImportError:
            print("❌ MSS not installed: pip install mss")
        except Exception as e:
            print(f"❌ MSS initialization failed: {e}")
        return False
    
    def _init_pyautogui(self) -> bool:
        """Initialize PyAutoGUI screenshot method"""
        try:
            import pyautogui
            test_img = pyautogui.screenshot(region=(0, 0, 100, 100))
            if test_img:
                print("✅ PyAutoGUI screenshot method initialized")
                self._initialized = True
                return True
        except ImportError:
            print("❌ PyAutoGUI not installed: pip install pyautogui")
        except Exception as e:
            print(f"❌ PyAutoGUI initialization failed: {e}")
        return False
    
    def capture_full_screen(self) -> Optional[bytes]:
        """Capture full screen screenshot"""
        if not self._initialized:
            print("❌ Screenshot capture not initialized")
            return None
        
        try:
            if self.method == 'wsl_powershell':
                return self._capture_wsl_powershell()
            elif self.method == 'windows_native':
                return self._capture_windows_native()
            elif self.method == 'mss':
                return self._capture_mss()
            elif self.method == 'pyautogui':
                return self._capture_pyautogui()
            else:
                print(f"❌ Unknown screenshot method: {self.method}")
                return None
                
        except Exception as e:
            print(f"❌ Screenshot capture failed: {e}")
            return None
    
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> Optional[bytes]:
        """Capture a specific region of interest"""
        if not self._initialized:
            print("❌ Screenshot capture not initialized")
            return None
        
        left, top, right, bottom = roi
        
        # Validate ROI
        if left >= right or top >= bottom:
            print(f"❌ Invalid ROI coordinates: {roi}")
            return None
        
        try:
            if self.method == 'wsl_powershell':
                return self._capture_wsl_powershell_roi(roi)
            elif self.method == 'windows_native':
                return self._capture_windows_native_roi(roi)
            elif self.method == 'mss':
                return self._capture_mss_roi(roi)
            elif self.method == 'pyautogui':
                return self._capture_pyautogui_roi(roi)
            else:
                print(f"❌ Unknown screenshot method: {self.method}")
                return None
                
        except Exception as e:
            print(f"❌ ROI screenshot capture failed: {e}")
            return None
    
    def _capture_wsl_powershell(self) -> Optional[bytes]:
        """Capture screenshot using PowerShell in WSL"""
        ps_script = '''
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        $Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen
        $Width = $Screen.Width
        $Height = $Screen.Height
        $Left = $Screen.Left
        $Top = $Screen.Top
        
        try {
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
    
    def _capture_wsl_powershell_roi(self, roi: Tuple[int, int, int, int]) -> Optional[bytes]:
        """Capture ROI using PowerShell in WSL with multi-monitor support"""
        left, top, right, bottom = roi
        width = right - left
        height = bottom - top
        
        # Debug logging for multi-monitor troubleshooting (only on first capture)
        if not hasattr(self, '_debug_shown'):
            print(f"🔍 ROI capture initialized: {roi}")
            print(f"   - Coordinates: left={left}, top={top}, right={right}, bottom={bottom}")
            print(f"   - Size: {width}x{height}")
            self._debug_shown = True
        
        ps_script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        # Get virtual screen information to handle multi-monitor setups
        $Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen
        $VirtualLeft = $Screen.Left
        $VirtualTop = $Screen.Top
        $VirtualWidth = $Screen.Width
        $VirtualHeight = $Screen.Height
        
        # Get all monitors for detailed debugging
        $Monitors = [System.Windows.Forms.Screen]::AllScreens
        Write-Host "=== MULTI-MONITOR DEBUG ===" -ForegroundColor Yellow
        Write-Host "Virtual Screen: Left=$VirtualLeft, Top=$VirtualTop, Width=$VirtualWidth, Height=$VirtualHeight" -ForegroundColor Cyan
        Write-Host "Number of monitors: $($Monitors.Count)" -ForegroundColor Cyan
        
        for ($i = 0; $i -lt $Monitors.Count; $i++) {{
            $Monitor = $Monitors[$i]
            $Bounds = $Monitor.Bounds
            Write-Host "Monitor $($i + 1): X=$($Bounds.X), Y=$($Bounds.Y), Width=$($Bounds.Width), Height=$($Bounds.Height), Primary=$($Monitor.Primary)" -ForegroundColor Cyan
        }}
        
        # ROI coordinates (from web interface, these are screen coordinates)
        $ROILeft = {left}
        $ROITop = {top}
        $ROIWidth = {width}
        $ROIHeight = {height}
        
        Write-Host "Original ROI: Left=$ROILeft, Top=$ROITop, Width=$ROIWidth, Height=$ROIHeight" -ForegroundColor Magenta
        
        # Use ROI coordinates directly - they are already screen coordinates from the web interface
        # The web interface captures coordinates from a full-screen screenshot, so they should be absolute
        $CaptureLeft = $ROILeft
        $CaptureTop = $ROITop
        
        Write-Host "Capture coordinates: Left=$CaptureLeft, Top=$CaptureTop, Width=$ROIWidth, Height=$ROIHeight" -ForegroundColor Green
        
        # Validate capture area is within virtual screen bounds
        $MaxX = $VirtualLeft + $VirtualWidth
        $MaxY = $VirtualTop + $VirtualHeight
        
        if ($CaptureLeft -lt $VirtualLeft -or $CaptureTop -lt $VirtualTop -or 
            ($CaptureLeft + $ROIWidth) -gt $MaxX -or ($CaptureTop + $ROIHeight) -gt $MaxY) {{
            Write-Host "WARNING: ROI extends beyond virtual screen bounds!" -ForegroundColor Red
            Write-Host "Virtual bounds: $VirtualLeft,$VirtualTop to $MaxX,$MaxY" -ForegroundColor Red
            Write-Host "ROI bounds: $CaptureLeft,$CaptureTop to $($CaptureLeft + $ROIWidth),$($CaptureTop + $ROIHeight)" -ForegroundColor Red
        }}
        
        try {{
            $bitmap = New-Object System.Drawing.Bitmap $ROIWidth, $ROIHeight
            $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
            
            Write-Host "Attempting CopyFromScreen($CaptureLeft, $CaptureTop, 0, 0, Size($ROIWidth, $ROIHeight))" -ForegroundColor Yellow
            $graphic.CopyFromScreen($CaptureLeft, $CaptureTop, 0, 0, $bitmap.Size)
            
            $ms = New-Object System.IO.MemoryStream
            $bitmap.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
            $bytes = $ms.ToArray()
            $base64 = [Convert]::ToBase64String($bytes)
            
            Write-Host "Capture successful: $($bytes.Length) bytes" -ForegroundColor Green
            Write-Output $base64
        }} catch {{
            Write-Host "Capture failed: $($_.Exception.Message)" -ForegroundColor Red
            Write-Error $_.Exception.Message
            exit 1
        }} finally {{
            if ($graphic) {{ $graphic.Dispose() }}
            if ($bitmap) {{ $bitmap.Dispose() }}
            if ($ms) {{ $ms.Dispose() }}
        }}
        '''
        
        result = self._execute_powershell_script(ps_script, f"ROI capture {roi}")
        if result:
            # Only show detailed success on first capture or every 10th capture
            if not hasattr(self, '_capture_count'):
                self._capture_count = 0
            self._capture_count += 1
            if self._capture_count == 1 or self._capture_count % 10 == 0:
                print(f"✅ ROI capture successful: {len(result)} bytes (capture #{self._capture_count})")
        return result
    
    def _execute_powershell_script(self, script: str, operation: str) -> Optional[bytes]:
        """Execute a PowerShell script and return the result as bytes"""
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
                
                # Print PowerShell debug output if available
                if result.stderr.strip():
                    print(f"🔍 PowerShell debug: {result.stderr.strip()}")
                
                return screenshot_bytes
            else:
                print(f"❌ PowerShell {operation} failed: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print(f"❌ PowerShell {operation} timed out")
            return None
        except Exception as e:
            print(f"❌ PowerShell {operation} error: {e}")
            return None
    
    def _capture_windows_native(self) -> Optional[bytes]:
        """Capture screenshot using Windows native method"""
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab()
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
            
        except Exception as e:
            print(f"❌ Windows native capture error: {e}")
            return None
    
    def _capture_windows_native_roi(self, roi: Tuple[int, int, int, int]) -> Optional[bytes]:
        """Capture ROI using Windows native method"""
        try:
            from PIL import ImageGrab
            img = ImageGrab.grab(bbox=roi)
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
            
        except Exception as e:
            print(f"❌ Windows native ROI capture error: {e}")
            return None
    
    def _capture_mss(self) -> Optional[bytes]:
        """Capture screenshot using MSS"""
        try:
            import mss
            with mss.mss() as sct:
                img = sct.grab(sct.monitors[0])  # All monitors
                
                pil_img = Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX')
                img_bytes = io.BytesIO()
                pil_img.save(img_bytes, format='PNG')
                return img_bytes.getvalue()
                
        except Exception as e:
            print(f"❌ MSS capture error: {e}")
            return None
    
    def _capture_mss_roi(self, roi: Tuple[int, int, int, int]) -> Optional[bytes]:
        """Capture ROI using MSS"""
        try:
            import mss
            left, top, right, bottom = roi
            
            with mss.mss() as sct:
                monitor = {
                    'left': left,
                    'top': top,
                    'width': right - left,
                    'height': bottom - top
                }
                img = sct.grab(monitor)
                
                pil_img = Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX')
                img_bytes = io.BytesIO()
                pil_img.save(img_bytes, format='PNG')
                return img_bytes.getvalue()
                
        except Exception as e:
            print(f"❌ MSS ROI capture error: {e}")
            return None
    
    def _capture_pyautogui(self) -> Optional[bytes]:
        """Capture screenshot using PyAutoGUI"""
        try:
            import pyautogui
            pyautogui.FAILSAFE = False  # Disable fail-safe for automation
            
            img = pyautogui.screenshot()
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
            
        except Exception as e:
            print(f"❌ PyAutoGUI capture error: {e}")
            return None
    
    def _capture_pyautogui_roi(self, roi: Tuple[int, int, int, int]) -> Optional[bytes]:
        """Capture ROI using PyAutoGUI"""
        try:
            import pyautogui
            pyautogui.FAILSAFE = False  # Disable fail-safe for automation
            
            left, top, right, bottom = roi
            width = right - left
            height = bottom - top
            
            img = pyautogui.screenshot(region=(left, top, width, height))
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            return img_bytes.getvalue()
            
        except Exception as e:
            print(f"❌ PyAutoGUI ROI capture error: {e}")
            return None


# Legacy functions for backward compatibility
def take_screenshot(roi: Tuple[int, int, int, int] = None) -> Optional[bytes]:
    """Legacy function for taking screenshots"""
    from ..config.config import Config
    
    config = Config()
    capture = ScreenshotCapture(config)
    
    if not capture.initialize():
        return None
    
    if roi:
        return capture.capture_roi(roi)
    else:
        return capture.capture_full_screen()


def take_full_screenshot(save_to_temp: bool = False) -> Optional[bytes]:
    """Legacy function for taking full screenshots"""
    from ..config.config import Config
    
    config = Config()
    capture = ScreenshotCapture(config)
    
    if not capture.initialize():
        return None
    
    screenshot = capture.capture_full_screen()
    
    if screenshot and save_to_temp:
        try:
            temp_path = config.temp_screenshot_path
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, 'wb') as f:
                f.write(screenshot)
        except Exception as e:
            print(f"❌ Failed to save temp screenshot: {e}")
    
    return screenshot
