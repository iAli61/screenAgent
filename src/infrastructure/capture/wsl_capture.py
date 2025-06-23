"""
WSL-specific screenshot capture implementation
Uses PowerShell bridge to capture Windows desktop from WSL
"""
import os
import subprocess
import base64
from typing import Tuple, Dict, Any

from . import ICaptureHandler, CaptureResult, CaptureMethod, CaptureCapabilities


class WSLPowerShellCapture(ICaptureHandler):
    """WSL screenshot capture using PowerShell bridge"""
    
    def __init__(self):
        super().__init__()
        self._capabilities = CaptureCapabilities(
            method=CaptureMethod.WSL_POWERSHELL,
            supports_roi=True,
            supports_multi_monitor=True,
            requires_elevated=False,
            performance_rating=3,
            reliability_rating=4,
            platform_specific=True
        )
    
    def can_handle(self) -> bool:
        """Check if WSL with PowerShell is available"""
        # Check for WSL environment
        if 'WSL_DISTRO_NAME' not in os.environ:
            try:
                with open('/proc/version', 'r') as f:
                    content = f.read().lower()
                    if 'microsoft' not in content and 'wsl' not in content:
                        print("Not running in WSL environment (can_handle)")
                        return False
            except Exception as e:
                print(f"Error checking WSL in /proc/version: {e}")
                return False
        
        # Test PowerShell availability
        try:
            print("Testing PowerShell availability...")
            result = subprocess.run(
                ['powershell.exe', '-Command', 'echo "test"'],
                capture_output=True,
                timeout=5,
                text=True
            )
            ps_available = result.returncode == 0
            if ps_available:
                print("✅ PowerShell is available")
            else:
                print(f"❌ PowerShell test failed: {result.stderr}")
            return ps_available
        except Exception as e:
            print(f"❌ PowerShell test error: {e}")
            return False
    
    def initialize(self) -> bool:
        """Initialize WSL PowerShell capture"""
        try:
            # First, verify we're running in WSL
            if 'WSL_DISTRO_NAME' not in os.environ:
                with open('/proc/version', 'r') as f:
                    content = f.read().lower()
                    if 'microsoft' not in content and 'wsl' not in content:
                        print("Not running in WSL environment")
                        return False
                
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
            
            print(f"PowerShell test failed: {result.stderr}")
            return False
            
        except Exception as e:
            print(f"WSL PowerShell capture initialization failed: {e}")
            return False
    
    def _capture_full_screen(self) -> CaptureResult:
        """Capture full screen using PowerShell from WSL"""
        ps_script = '''
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        try {
            # Get information about the virtual screen (all monitors combined)
            $VirtualScreen = [System.Windows.Forms.SystemInformation]::VirtualScreen
            $VirtualWidth = $VirtualScreen.Width
            $VirtualHeight = $VirtualScreen.Height
            $VirtualLeft = $VirtualScreen.Left
            $VirtualTop = $VirtualScreen.Top
            
            # Get information about all screens
            $AllScreens = [System.Windows.Forms.Screen]::AllScreens
            $PrimaryScreen = [System.Windows.Forms.Screen]::PrimaryScreen
            
            # Debug output
            Write-Output "DEBUG_START"
            Write-Output "Virtual Screen: $VirtualLeft, $VirtualTop, $VirtualWidth x $VirtualHeight"
            Write-Output "Number of screens: $($AllScreens.Length)"
            foreach ($screen in $AllScreens) {
                Write-Output "Screen: $($screen.Bounds.X), $($screen.Bounds.Y), $($screen.Bounds.Width) x $($screen.Bounds.Height), Primary: $($screen.Primary)"
            }
            Write-Output "DEBUG_END"

            # Create bitmap to hold the screenshot
            $bitmap = New-Object System.Drawing.Bitmap $VirtualWidth, $VirtualHeight
            $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
            
            # Set high quality settings
            $graphic.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $graphic.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $graphic.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
            
            # Capture the entire virtual screen
            $graphic.CopyFromScreen($VirtualLeft, $VirtualTop, 0, 0, $bitmap.Size)
            
            # Convert to PNG
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
        """Capture ROI using PowerShell from WSL"""
        left, top, right, bottom = roi
        width = right - left
        height = bottom - top
        
        ps_script = f'''
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        try {{
            # Get information about the virtual screen (all monitors combined)
            $VirtualScreen = [System.Windows.Forms.SystemInformation]::VirtualScreen
            $VirtualLeft = $VirtualScreen.Left
            $VirtualTop = $VirtualScreen.Top
            
            # Create bitmap to hold the screenshot
            $bitmap = New-Object System.Drawing.Bitmap {width}, {height}
            $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
            
            # Set high quality settings
            $graphic.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $graphic.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $graphic.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality

            # Take into account the virtual screen coordinates offset
            $captureLeft = {left} 
            $captureTop = {top}
            
            # Debug info
            Write-Output "DEBUG_START"
            Write-Output "ROI: {left}, {top}, {width} x {height}"
            Write-Output "Virtual Screen Offset: $VirtualLeft, $VirtualTop"
            Write-Output "Capture: $captureLeft, $captureTop, {width} x {height}"
            Write-Output "DEBUG_END"
            
            # Capture the region
            $graphic.CopyFromScreen($captureLeft, $captureTop, 0, 0, $bitmap.Size)
            
            # Convert to PNG
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
        """Execute PowerShell script from WSL and return capture result"""
        try:
            print(f"📷 Executing PowerShell capture for {operation}...")
            result = subprocess.run(
                ['powershell.exe', '-Command', script],
                capture_output=True,
                timeout=60,  # Increase timeout for large screenshots
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                output = result.stdout.strip()
                
                # Check for debug output and log it
                debug_start = output.find('DEBUG_START')
                debug_end = output.find('DEBUG_END')
                
                if debug_start >= 0 and debug_end > debug_start:
                    debug_info = output[debug_start + len('DEBUG_START'):debug_end].strip()
                    print(f"🖥️ Monitor Configuration:")
                    for line in debug_info.split('\n'):
                        print(f"  {line.strip()}")
                    
                    # Remove debug info from output
                    base64_start = debug_end + len('DEBUG_END')
                    base64_data = output[base64_start:].strip()
                else:
                    base64_data = output
                
                # Decode base64 data
                try:
                    if not base64_data:
                        print(f"❌ Empty base64 data received from PowerShell")
                        return CaptureResult(False, error="Empty image data received from PowerShell")
                    
                    print(f"📷 Received base64 data (length: {len(base64_data)})")
                    image_data = base64.b64decode(base64_data)
                    print(f"✅ Successfully decoded image data (size: {len(image_data)} bytes)")
                    
                    metadata = {
                        'method': 'wsl_powershell',
                        'operation': operation,
                        'size': len(image_data),
                        'environment': 'wsl'
                    }
                    
                    return CaptureResult(True, image_data, metadata=metadata)
                except Exception as e:
                    return CaptureResult(False, error=f"Failed to decode base64 data: {e}")
            else:
                error_msg = result.stderr if result.stderr else "PowerShell script failed"
                return CaptureResult(False, error=f"WSL PowerShell {operation} failed: {error_msg}")
                
        except subprocess.TimeoutExpired:
            return CaptureResult(False, error=f"WSL PowerShell {operation} timed out")
        except Exception as e:
            return CaptureResult(False, error=f"WSL PowerShell {operation} error: {str(e)}")
    
    # Add compatibility methods for direct access from CaptureServiceImpl
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Direct capture ROI method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="WSL PowerShell capture not initialized")
        return self._capture_roi(roi)
    
    def capture_full_screen(self) -> CaptureResult:
        """Direct capture full screen method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="WSL PowerShell capture not initialized")
        return self._capture_full_screen()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self._initialized = False


class WSLPyAutoGUICapture(ICaptureHandler):
    """WSL screenshot capture using PyAutoGUI fallback"""
    
    def __init__(self):
        super().__init__()
        self._capabilities = CaptureCapabilities(
            method=CaptureMethod.PYAUTOGUI,
            supports_roi=True,
            supports_multi_monitor=False,  # PyAutoGUI has limited multi-monitor support
            requires_elevated=False,
            performance_rating=2,
            reliability_rating=3,
            platform_specific=False
        )
        self._pyautogui = None
    
    def can_handle(self) -> bool:
        """Check if PyAutoGUI is available in WSL"""
        try:
            # Check if we're in WSL environment first
            if 'WSL_DISTRO_NAME' not in os.environ:
                with open('/proc/version', 'r') as f:
                    content = f.read().lower()
                    if 'microsoft' not in content and 'wsl' not in content:
                        print("Not running in WSL environment for PyAutoGUI")
                        return False
                        
            # Check if PyAutoGUI is installed
            try:
                import pyautogui
                print("✅ PyAutoGUI is available")
                return True
            except ImportError:
                print("❌ PyAutoGUI is not installed")
                return False
        except Exception as e:
            print(f"❌ Error checking PyAutoGUI: {e}")
            return False
    
    def initialize(self) -> bool:
        """Initialize PyAutoGUI capture"""
        try:
            print("Initializing PyAutoGUI capture...")
            import pyautogui
            # Disable fail-safe
            pyautogui.FAILSAFE = False
            self._pyautogui = pyautogui
            
            # Test if we can get screen size
            try:
                width, height = self._pyautogui.size()
                if width > 0 and height > 0:
                    print(f"✅ PyAutoGUI detected screen size: {width}x{height}")
                    self._initialized = True
                    return True
                else:
                    print("❌ PyAutoGUI returned invalid screen size")
            except Exception as e:
                print(f"❌ Error getting screen size with PyAutoGUI: {e}")
            
            return False
            
        except Exception as e:
            print(f"❌ WSL PyAutoGUI capture initialization failed: {e}")
            return False
    
    def _capture_full_screen(self) -> CaptureResult:
        """Capture full screen using PyAutoGUI"""
        try:
            import io
            
            # Take screenshot
            screenshot = self._pyautogui.screenshot()
            
            # Convert to PNG bytes
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format='PNG')
            image_data = img_buffer.getvalue()
            
            metadata = {
                'method': 'pyautogui',
                'operation': 'full_screen',
                'size': len(image_data),
                'environment': 'wsl'
            }
            
            return CaptureResult(True, image_data, metadata=metadata)
            
        except Exception as e:
            return CaptureResult(False, error=f"WSL PyAutoGUI full screen capture failed: {str(e)}")
    
    def _capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Capture ROI using PyAutoGUI"""
        try:
            import io
            
            left, top, right, bottom = roi
            width = right - left
            height = bottom - top
            
            # Take screenshot of region
            screenshot = self._pyautogui.screenshot(region=(left, top, width, height))
            
            # Convert to PNG bytes
            img_buffer = io.BytesIO()
            screenshot.save(img_buffer, format='PNG')
            image_data = img_buffer.getvalue()
            
            metadata = {
                'method': 'pyautogui',
                'operation': 'roi_capture',
                'roi': roi,
                'size': len(image_data),
                'environment': 'wsl'
            }
            
            return CaptureResult(True, image_data, metadata=metadata)
            
        except Exception as e:
            return CaptureResult(False, error=f"WSL PyAutoGUI ROI capture failed: {str(e)}")
    
    # Add compatibility methods for direct access from CaptureServiceImpl
    def capture_roi(self, roi: Tuple[int, int, int, int]) -> CaptureResult:
        """Direct capture ROI method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="WSL PyAutoGUI capture not initialized")
        return self._capture_roi(roi)
    
    def capture_full_screen(self) -> CaptureResult:
        """Direct capture full screen method for CaptureServiceImpl"""
        if not self._initialized:
            return CaptureResult(False, error="WSL PyAutoGUI capture not initialized")
        return self._capture_full_screen()
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self._pyautogui = None
        self._initialized = False
