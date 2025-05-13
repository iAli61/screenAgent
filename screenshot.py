import io
import subprocess
import os
import sys
from PIL import Image, ImageDraw
from platform_detection import WSL_MODE

# Screenshot method initialization
SCREENSHOT_METHOD = None
KEYBOARD_AVAILABLE = False

def setup_screenshot_method():
    """Initialize the appropriate screenshot method based on environment"""
    global SCREENSHOT_METHOD
    if WSL_MODE:
        setup_wsl_screenshot()
    elif os.geteuid() == 0:
        setup_root_screenshot()
    else:
        setup_default_screenshot()

def setup_wsl_screenshot():
    """Configure WSL-specific screenshot method"""
    global SCREENSHOT_METHOD
    try:
        import subprocess
        import base64
        SCREENSHOT_METHOD = "wsl_powershell"
        print("Using WSL PowerShell method for screenshots")
    except Exception as e:
        print(f"Failed to set up WSL screenshot method: {e}")

def setup_root_screenshot():
    """Configure screenshot method when running as root"""
    global SCREENSHOT_METHOD
    try:
        import mss
        SCREENSHOT_METHOD = "mss"
        print("Using MSS library for screenshots (root mode)")
    except ImportError:
        print("MSS not available, please install: pip install mss")

def setup_default_screenshot():
    """Configure default screenshot method"""
    global SCREENSHOT_METHOD
    try:
        import pyautogui
        SCREENSHOT_METHOD = "pyautogui"
        print("Using PyAutoGUI for screenshots")
    except ImportError:
        try:
            from PIL import ImageGrab
            SCREENSHOT_METHOD = "pillow"
            print("Using PIL ImageGrab for screenshots")
        except (ImportError, OSError) as e:
            print(f"Warning: Could not initialize screenshot capabilities: {e}")
            print("Please install one of these libraries:")
            print("- pip install pyautogui (recommended)")
            print("- pip install mss (Linux alternative)")
            print("- For PIL/Pillow with XCB: pip install --upgrade pillow-xcb")
            sys.exit(1)

def wsl_powershell_screenshot(roi=None, save_to_temp=False):
    """Use PowerShell to take a screenshot in WSL
    
    Args:
        roi: Region of interest as (left, top, right, bottom)
        save_to_temp: If True, save the screenshot to temp file and don't delete it
    """
    # Import the correct temporary screenshot path
    from config import TEMP_SCREENSHOT_PATH
    
    try:
        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ps_script_path = os.path.join(current_dir, "screenshot_script.ps1")
        
        # Instead of saving to a file and executing it, we'll run the PowerShell
        # script content directly to avoid path translation issues
        ps_script = """
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        
        $Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen
        $Width = $Screen.Width
        $Height = $Screen.Height
        $Left = $Screen.Left
        $Top = $Screen.Top
        
        try {
            # Create bitmap and grab screen
            $bitmap = New-Object System.Drawing.Bitmap $Width, $Height
            $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphic.CopyFromScreen($Left, $Top, 0, 0, $bitmap.Size)
            
            # Convert to base64 string
            $ms = New-Object System.IO.MemoryStream
            $bitmap.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
            $bytes = $ms.ToArray()
            $base64 = [Convert]::ToBase64String($bytes)
            
            # Output the base64 string
            Write-Output $base64
            $bitmap.Dispose()
            $ms.Dispose()
        }
        catch {
            Write-Error "Failed to capture screenshot: $_"
            exit 1
        }
        """
        
        # Execute PowerShell script directly as a command, not as a file
        print(f"Executing PowerShell script to capture screenshot")
        result = subprocess.run(
            ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
            capture_output=True, text=True
        )
        
        if result.returncode != 0:
            print(f"PowerShell error: {result.stderr}")
            raise Exception(f"PowerShell execution failed: {result.stderr}")
        
        # The output should be a base64 string
        base64_data = result.stdout.strip()
        if not base64_data:
            raise Exception("No base64 data returned from PowerShell")
            
        # Convert base64 to image
        import base64
        image_data = base64.b64decode(base64_data)
        
        # Load image from bytes
        img = Image.open(io.BytesIO(image_data))
        
        # If save_to_temp is True, save the image
        if save_to_temp:
            img.save(TEMP_SCREENSHOT_PATH)
        
        # Crop if ROI specified
        if roi:
            img = img.crop(roi)
        
        # Convert to bytes for return
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        
        return img_byte_arr.getvalue()
        
    except Exception as e:
        print(f"PowerShell screenshot failed: {e}")
        # Fallback to placeholder image
        return create_placeholder_image(f"WSL Screenshot Error: {e}")

def take_full_screenshot(save_to_temp=False):
    """Capture the full screen and return as bytes
    
    Args:
        save_to_temp: If True, save the screenshot to temp file and don't delete it
    """
    try:
        if SCREENSHOT_METHOD == "wsl_powershell":
            # WSL-specific method for full screen
            return wsl_powershell_screenshot(save_to_temp=save_to_temp)
        elif SCREENSHOT_METHOD == "pyautogui":
            # PyAutoGUI method
            import pyautogui
            img = pyautogui.screenshot()
        elif SCREENSHOT_METHOD == "mss":
            # MSS method
            import mss
            with mss.mss() as sct:
                # Capture entire screen
                monitor = sct.monitors[0]  # Full screen
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        elif SCREENSHOT_METHOD == "pillow":
            # PIL/Pillow method
            from PIL import ImageGrab
            img = ImageGrab.grab()
        else:
            raise RuntimeError("No screenshot method available")

        # For non-WSL methods, if save_to_temp is True, save to temp file
        if save_to_temp and SCREENSHOT_METHOD != "wsl_powershell":
            from config import TEMP_SCREENSHOT_PATH
            img.save(TEMP_SCREENSHOT_PATH, format='PNG')

        # Return image bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception as e:
        print(f"Full screenshot error: {e}")
        return create_placeholder_image(f"Screenshot Error: {e}")

def take_screenshot(roi):
    """Capture the ROI and return as bytes"""
    try:
        if SCREENSHOT_METHOD == "wsl_powershell":
            # WSL-specific method
            return wsl_powershell_screenshot(roi)
        elif SCREENSHOT_METHOD == "pyautogui":
            # PyAutoGUI method
            import pyautogui
            img = pyautogui.screenshot(region=roi)
        elif SCREENSHOT_METHOD == "mss":
            # MSS method
            import mss
            with mss.mss() as sct:
                # Convert ROI format from (left, top, right, bottom) to (left, top, width, height)
                monitor = {"left": roi[0], "top": roi[1], 
                           "width": roi[2] - roi[0], "height": roi[3] - roi[1]}
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        elif SCREENSHOT_METHOD == "pillow":
            # PIL/Pillow method
            from PIL import ImageGrab
            img = ImageGrab.grab(bbox=roi)
        else:
            raise RuntimeError("No screenshot method available")

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception as e:
        print(f"Screenshot error: {e}")
        return create_placeholder_image(f"Screenshot Error: {e}")

def create_placeholder_image(message):
    """Create a placeholder image with an error message"""
    img = Image.new('RGB', (300, 200), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10, 10), message, fill=(255, 255, 0))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

# Initialize screenshot method
setup_screenshot_method()