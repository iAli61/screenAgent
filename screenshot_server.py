import io
import time
import threading
import http.server
import socketserver
import numpy as np
import socket
from datetime import datetime
import os
import sys
import json
from PIL import Image, ImageDraw

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screen_agent_config.json')

# Save and load ROI configuration functions
def save_roi_to_config(roi):
    """Save ROI settings to a configuration file"""
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            # If the file exists but is invalid, we'll overwrite it
            pass
    
    config['roi'] = roi
    
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print(f"ROI settings saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"Error saving ROI settings: {e}")
        return False

def load_roi_from_config():
    """Load ROI settings from configuration file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                if 'roi' in config and len(config['roi']) == 4:
                    print(f"ROI settings loaded from {CONFIG_FILE}")
                    return tuple(config['roi'])
        except Exception as e:
            print(f"Error loading ROI settings: {e}")
    
    return None

# Detect if running in WSL
def is_wsl():
    if os.path.exists('/proc/version'):
        with open('/proc/version', 'r') as f:
            if "microsoft" in f.read().lower():
                print("Running in WSL environment")
                return True
    return False

WSL_MODE = is_wsl()

# Use platform-specific screenshot methods
SCREENSHOT_METHOD = None
KEYBOARD_AVAILABLE = False

# For WSL, we need to use a different approach since it doesn't have direct access to the X server
if WSL_MODE:
    try:
        # Try to use PowerShell commands to take screenshots
        print("Setting up WSL screenshot method using PowerShell")
        import subprocess
        import base64
        
        def wsl_powershell_screenshot(roi=None):
            """Use PowerShell to take a screenshot in WSL"""
            temp_file = os.path.join(os.path.expanduser("~"), "temp_screenshot.png")
            
            # Create PowerShell script to take screenshot
            ps_script = """
            Add-Type -AssemblyName System.Windows.Forms
            Add-Type -AssemblyName System.Drawing
            
            $Screen = [System.Windows.Forms.SystemInformation]::VirtualScreen
            $Width = $Screen.Width
            $Height = $Screen.Height
            $Left = $Screen.Left
            $Top = $Screen.Top
            
            $bitmap = New-Object System.Drawing.Bitmap $Width, $Height
            $graphic = [System.Drawing.Graphics]::FromImage($bitmap)
            $graphic.CopyFromScreen($Left, $Top, 0, 0, $bitmap.Size)
            
            $bitmap.Save('{0}', [System.Drawing.Imaging.ImageFormat]::Png)
            Write-Output "Screenshot saved to {0}"
            """.format(temp_file.replace('\\', '\\\\'))
            
            # Save script to temporary file
            ps_script_path = os.path.join(os.path.expanduser("~"), "screenshot_script.ps1")
            with open(ps_script_path, 'w') as f:
                f.write(ps_script)
            
            # Execute PowerShell script
            try:
                subprocess.run(['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', ps_script_path], 
                               check=True)
                
                # Read the screenshot and crop to ROI if specified
                if os.path.exists(temp_file):
                    img = Image.open(temp_file)
                    if roi:
                        img = img.crop(roi)
                    
                    # Convert to bytes
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    
                    # Clean up
                    os.remove(temp_file)
                    os.remove(ps_script_path)
                    
                    return img_byte_arr.getvalue()
                else:
                    raise FileNotFoundError(f"Screenshot file not found at {temp_file}")
            except Exception as e:
                print(f"PowerShell screenshot failed: {e}")
                # Create a dummy screenshot with error message
                img = Image.new('RGB', (800, 600), color=(50, 50, 50))
                d = ImageDraw.Draw(img)
                d.text((10, 10), f"WSL Screenshot Error: {e}", fill=(255, 0, 0))
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG')
                return img_byte_arr.getvalue()
        
        SCREENSHOT_METHOD = "wsl_powershell"
        print("Using WSL PowerShell method for screenshots")
    except Exception as e:
        print(f"Failed to set up WSL screenshot method: {e}")
        print("Please install Windows PowerShell for WSL screenshot support")
elif os.geteuid() == 0:  # Running as root/sudo (but not in WSL)
    print("Running with sudo/root privileges")
    # Try to use MSS first when running as root as it has fewer X11 dependencies
    try:
        import mss
        SCREENSHOT_METHOD = "mss"
        print("Using MSS library for screenshots (root mode)")
    except ImportError:
        print("MSS not available, please install: pip install mss")
    
    # If XAUTHORITY is not set in environment and we're running as root
    if SCREENSHOT_METHOD is None and 'XAUTHORITY' not in os.environ:
        # Try to find the non-root user's .Xauthority file
        sudo_user = os.environ.get('SUDO_USER')
        if sudo_user:
            user_home = os.path.expanduser(f'~{sudo_user}')
            xauth_path = os.path.join(user_home, '.Xauthority')
            if os.path.exists(xauth_path):
                os.environ['XAUTHORITY'] = xauth_path
                print(f"Set XAUTHORITY to {xauth_path}")
    
    # Make sure DISPLAY is set
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
        print("Set DISPLAY to :0")
else:
    # Not running as root or in WSL, try PyAutoGUI first if available
    try:
        import pyautogui
        SCREENSHOT_METHOD = "pyautogui"
        print("Using PyAutoGUI for screenshots")
    except ImportError:
        pass

# If screenshot method is still not set, try alternatives
if not SCREENSHOT_METHOD:
    if sys.platform == 'linux':
        try:
            # Try using mss library which works on Linux without XCB dependency
            import mss
            SCREENSHOT_METHOD = "mss"
            print("Using MSS library for screenshots")
        except ImportError:
            pass
            
    # Try PIL as a last resort
    if not SCREENSHOT_METHOD:
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

# Configure keyboard handling
if WSL_MODE:
    # In WSL, keyboard module won't work properly with Windows - disable it
    KEYBOARD_AVAILABLE = False
    print("Keyboard shortcuts not available in WSL mode")
else:
    # Try to import keyboard, but handle the case where it requires root privileges
    try:
        import keyboard
        KEYBOARD_AVAILABLE = True
        TRIGGER_KEY = 'f12'  # Key to trigger a screenshot manually
        print("Keyboard shortcuts enabled")
    except ImportError as e:
        KEYBOARD_AVAILABLE = False
        print(f"Keyboard module not available: {e}")
        print("Run with sudo for keyboard shortcuts or use web interface.")

# Configuration
PORT = 8000
MAX_PORT_ATTEMPTS = 10  # Try up to 10 ports if the initial one is in use
ROI = load_roi_from_config() or (100, 100, 400, 400)  # (left, top, right, bottom)
CHANGE_THRESHOLD = 20  # Pixel difference threshold to trigger screenshot
CHECK_INTERVAL = 0.5  # Seconds between checks for ROI changes
TEMP_SCREENSHOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_screenshot.png')

# Storage for screenshots
screenshots = []
last_screenshot = None
is_selecting_roi = False  # Flag to indicate if the user is currently selecting ROI

def store_temp_screenshot(screenshot_bytes):
    """Store a temporary screenshot for ROI selection"""
    try:
        with open(TEMP_SCREENSHOT_PATH, 'wb') as f:
            f.write(screenshot_bytes)
        return True
    except Exception as e:
        print(f"Error storing temporary screenshot: {e}")
        return False

def delete_temp_screenshot():
    """Delete the temporary screenshot file if it exists"""
    if os.path.exists(TEMP_SCREENSHOT_PATH):
        try:
            os.remove(TEMP_SCREENSHOT_PATH)
            return True
        except Exception as e:
            print(f"Error deleting temporary screenshot: {e}")
    return False

class ScreenshotHandler(http.server.BaseHTTPRequestHandler):
    # Helper to parse JSON from POST requests
    def parse_json_body(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        return json.loads(post_data.decode('utf-8'))
    
    def do_POST(self):
        global ROI
        
        if self.path == '/set_roi':
            # Handle setting ROI via POST with JSON payload
            try:
                roi_data = self.parse_json_body()
                
                # Validate ROI data
                if 'roi' in roi_data and len(roi_data['roi']) == 4:
                    left, top, right, bottom = roi_data['roi']
                    
                    # Make sure values are integers
                    left, top, right, bottom = int(left), int(top), int(right), int(bottom)
                    
                    # Validate the ROI dimensions
                    if left < right and top < bottom and right - left > 10 and bottom - top > 10:
                        ROI = (left, top, right, bottom)
                        save_roi_to_config(ROI)
                        print(f"ROI updated to {ROI}")
                        
                        # Send success response
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({'success': True, 'roi': ROI}).encode())
                        
                        # Clean up the temporary screenshot
                        delete_temp_screenshot()
                        return
                
                # If we get here, something was wrong with the ROI data
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': 'Invalid ROI'}).encode())
                
            except Exception as e:
                print(f"Error processing ROI POST data: {e}")
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
                
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        global ROI  # Declare ROI as global at the beginning of the method
        
        if self.path == '/':
            # Main page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Get the latest screenshot for the ROI preview
            latest_screenshot = None
            latest_screenshot_idx = -1
            if screenshots:
                latest_screenshot_idx = len(screenshots) - 1
                latest_screenshot = screenshots[latest_screenshot_idx][1]
            
            # Create HTML response with ROI preview
            html = """
            <html>
            <head>
                <title>ROI Screenshot Server</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                    }
                    .preview-container {
                        position: relative;
                        margin: 20px 0;
                        display: inline-block;
                    }
                    .roi-overlay {
                        position: absolute;
                        border: 2px solid red;
                        background-color: rgba(255, 0, 0, 0.2);
                    }
                    .button {
                        background-color: #4CAF50;
                        border: none;
                        color: white;
                        padding: 10px 15px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin: 4px 2px;
                        cursor: pointer;
                        border-radius: 4px;
                    }
                    .screenshot-list {
                        margin-top: 20px;
                        max-height: 300px;
                        overflow-y: auto;
                    }
                </style>
            </head>
            <body>
                <h1>ROI Screenshot Server</h1>
                <p>Monitoring ROI: """ + str(ROI) + """</p>
                
                <div class="preview-container">
                    <h3>Current ROI Preview:</h3>
                    """ + (f"""
                    <div style="position: relative; display: inline-block;">
                        <img src="/screenshot/{latest_screenshot_idx}" style="max-width: 400px; border: 1px solid #ddd;" />
                        <div id="roi-overlay" class="roi-overlay"></div>
                    </div>
                    <script>
                        // Calculate the position and size of the ROI overlay
                        window.onload = function() {{
                            const img = document.querySelector('.preview-container img');
                            const overlay = document.getElementById('roi-overlay');
                            const roi = {ROI};
                            
                            // Wait for image to load to get dimensions
                            img.onload = function() {{
                                const imgWidth = img.width;
                                const imgHeight = img.height;
                                const imgNaturalWidth = img.naturalWidth;
                                const imgNaturalHeight = img.naturalHeight;
                                
                                // Calculate the scale factor
                                const scaleX = imgWidth / imgNaturalWidth;
                                const scaleY = imgHeight / imgNaturalHeight;
                                
                                // Position the overlay based on the ROI and scale
                                overlay.style.left = (roi[0] * scaleX) + 'px';
                                overlay.style.top = (roi[1] * scaleY) + 'px';
                                overlay.style.width = ((roi[2] - roi[0]) * scaleX) + 'px';
                                overlay.style.height = ((roi[3] - roi[1]) * scaleY) + 'px';
                            }};
                        }};
                    </script>
                    """ if latest_screenshot else "<p>No screenshots available yet</p>") + """
                    <br>
                    <a href="/select_roi" class="button">Select New ROI</a>
                </div>
                
                <div>
                    <a href="/trigger" class="button">Take Screenshot Now</a>
                    """ + (f"<p>Press '{TRIGGER_KEY}' to take a screenshot</p>" if KEYBOARD_AVAILABLE else "") + """
                </div>
                
                <h2>Screenshots</h2>
                <div class="screenshot-list">
            """
            
            # List screenshots
            for i, (timestamp, _) in enumerate(screenshots):
                html += f'<p><a href="/screenshot/{i}">{timestamp}</a></p>'
            
            html += """
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
        
        elif self.path == '/trigger':
            # Manual screenshot endpoint
            new_screenshot = take_screenshot()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            screenshots.append((timestamp, new_screenshot))
            print(f"Manual screenshot taken at {timestamp}")
            
            # Redirect back to homepage
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            
        elif self.path == '/select_roi':
            # Take a full-screen screenshot for the background
            full_screenshot = take_full_screenshot()
            
            # Store it in the temporary file
            store_temp_screenshot(full_screenshot)
            
            # ROI selection page
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # ROI selection page with the full screenshot as background using canvas
            html = """
            <html>
            <head>
                <title>Select ROI</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    #canvas-container {
                        position: relative;
                        margin-top: 20px;
                        cursor: crosshair;
                        overflow: auto;
                        max-height: 80vh;
                        border: 1px solid #ccc;
                    }
                    canvas {
                        display: block;
                    }
                    #instructions {
                        background-color: rgba(255, 255, 255, 0.8);
                        padding: 10px;
                        margin: 10px 0;
                        border-radius: 5px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    }
                    .button {
                        background-color: #4CAF50;
                        border: none;
                        color: white;
                        padding: 10px 15px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 16px;
                        margin: 4px 2px;
                        cursor: pointer;
                        border-radius: 4px;
                    }
                    .button:disabled {
                        background-color: #cccccc;
                        cursor: not-allowed;
                    }
                    .cancel {
                        background-color: #f44336;
                    }
                    .controls {
                        margin-top: 15px;
                    }
                    .error {
                        color: red;
                        margin-top: 10px;
                    }
                </style>
            </head>
            <body>
                <h1>Select Region of Interest (ROI)</h1>
                <div id="instructions">
                    <p>Click and drag to select the area you want to monitor.</p>
                    <p>Selection must be at least 10x10 pixels.</p>
                    <p>Current ROI: <span id="roi-display">""" + str(ROI) + """</span></p>
                </div>
                <div id="canvas-container">
                    <canvas id="roi-canvas"></canvas>
                </div>
                <div class="controls">
                    <button id="set-roi-button" class="button" disabled>Set ROI</button>
                    <a href="/"><button class="button cancel">Cancel</button></a>
                    <div id="error-message" class="error"></div>
                </div>
                
                <script>
                    const canvas = document.getElementById('roi-canvas');
                    const ctx = canvas.getContext('2d');
                    const roiDisplay = document.getElementById('roi-display');
                    const setRoiButton = document.getElementById('set-roi-button');
                    const errorMessage = document.getElementById('error-message');
                    
                    let isSelecting = false;
                    let startX, startY;
                    let currentX, currentY;
                    let roi = null;
                    
                    // Load the screenshot image
                    const img = new Image();
                    img.src = '/temp_screenshot?' + new Date().getTime(); // Cache busting
                    
                    img.onload = function() {
                        // Set canvas size to match image
                        canvas.width = img.width;
                        canvas.height = img.height;
                        
                        // Draw the image initially
                        ctx.drawImage(img, 0, 0);
                        
                        // Draw initial ROI if available
                        const initialRoi = """ + str(ROI) + """;
                        drawRectangle(initialRoi[0], initialRoi[1], initialRoi[2], initialRoi[3], true);
                    };
                    
                    function validateRoi(left, top, right, bottom) {
                        if (right <= left || bottom <= top) {
                            errorMessage.textContent = 'Invalid selection: width and height must be positive.';
                            return false;
                        }
                        
                        if (right - left < 10 || bottom - top < 10) {
                            errorMessage.textContent = 'Selection too small: must be at least 10x10 pixels.';
                            return false;
                        }
                        
                        errorMessage.textContent = '';
                        return true;
                    }
                    
                    function drawRectangle(left, top, right, bottom, isInitial = false) {
                        // Redraw the image to clear previous rectangles
                        ctx.drawImage(img, 0, 0);
                        
                        // Draw the selection rectangle
                        ctx.strokeStyle = 'red';
                        ctx.lineWidth = 2;
                        ctx.strokeRect(left, top, right - left, bottom - top);
                        
                        // Add a semi-transparent fill
                        ctx.fillStyle = 'rgba(255, 0, 0, 0.2)';
                        ctx.fillRect(left, top, right - left, bottom - top);
                        
                        if (!isInitial) {
                            // Update ROI display and validation
                            roi = [left, top, right, bottom];
                            roiDisplay.textContent = `(${left}, ${top}, ${right}, ${bottom})`;
                            setRoiButton.disabled = !validateRoi(left, top, right, bottom);
                        }
                    }
                    
                    canvas.addEventListener('mousedown', (e) => {
                        const rect = canvas.getBoundingClientRect();
                        startX = e.clientX - rect.left;
                        startY = e.clientY - rect.top;
                        isSelecting = true;
                    });
                    
                    canvas.addEventListener('mousemove', (e) => {
                        if (!isSelecting) return;
                        
                        const rect = canvas.getBoundingClientRect();
                        currentX = e.clientX - rect.left;
                        currentY = e.clientY - rect.top;
                        
                        // Calculate rectangle coordinates
                        const left = Math.min(startX, currentX);
                        const top = Math.min(startY, currentY);
                        const right = Math.max(startX, currentX);
                        const bottom = Math.max(startY, currentY);
                        
                        // Draw the rectangle
                        drawRectangle(left, top, right, bottom);
                    });
                    
                    // Handle mouse up and mouse out the same way
                    function endSelection() {
                        if (!isSelecting) return;
                        isSelecting = false;
                        
                        // Final rectangle coordinates
                        const left = Math.min(startX, currentX);
                        const top = Math.min(startY, currentY);
                        const right = Math.max(startX, currentX);
                        const bottom = Math.max(startY, currentY);
                        
                        drawRectangle(left, top, right, bottom);
                    }
                    
                    canvas.addEventListener('mouseup', endSelection);
                    canvas.addEventListener('mouseout', endSelection);
                    
                    // Set ROI button click handler
                    setRoiButton.addEventListener('click', () => {
                        if (!roi) return;
                        
                        // Send ROI to server via POST
                        fetch('/set_roi', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ roi }),
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                window.location.href = '/';
                            } else {
                                errorMessage.textContent = data.error || 'Failed to set ROI';
                            }
                        })
                        .catch(error => {
                            errorMessage.textContent = 'Error: ' + error.message;
                        });
                    });
                </script>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

        elif self.path.startswith('/temp_screenshot'):
            # Serve the temporary screenshot for ROI selection
            if os.path.exists(TEMP_SCREENSHOT_PATH):
                with open(TEMP_SCREENSHOT_PATH, 'rb') as f:
                    screenshot_data = f.read()
                    
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(screenshot_data)
            else:
                self.send_response(404)
                self.end_headers()

        elif self.path.startswith('/screenshot/'):
            try:
                # Serve a specific screenshot
                idx = int(self.path.split('/')[-1])
                if 0 <= idx < len(screenshots):
                    self.send_response(200)
                    self.send_header('Content-type', 'image/png')
                    self.end_headers()
                    self.wfile.write(screenshots[idx][1])
                else:
                    self.send_response(404)
                    self.end_headers()
            except:
                self.send_response(404)
                self.end_headers()
        
        elif self.path.startswith('/set_roi'):
            # Handle GET requests to /set_roi (legacy support)
            # Redirect to the ROI selection page
            self.send_response(302)
            self.send_header('Location', '/select_roi')
            self.end_headers()
        
        else:
            self.send_response(404)
            self.end_headers()

def take_full_screenshot():
    """Capture the full screen and return as bytes"""
    try:
        if SCREENSHOT_METHOD == "wsl_powershell":
            # WSL-specific method for full screen
            return wsl_powershell_screenshot()
        elif SCREENSHOT_METHOD == "pyautogui":
            # PyAutoGUI method
            img = pyautogui.screenshot()
        elif SCREENSHOT_METHOD == "mss":
            # MSS method
            with mss.mss() as sct:
                # Capture entire screen
                monitor = sct.monitors[0]  # Full screen
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        elif SCREENSHOT_METHOD == "pillow":
            # PIL/Pillow method
            img = ImageGrab.grab()
        else:
            raise RuntimeError("No screenshot method available")

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception as e:
        print(f"Full screenshot error: {e}")
        # Return a placeholder image
        img = Image.new('RGB', (800, 600), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((10, 10), f"Screenshot Error: {e}", fill=(255, 255, 0))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

def take_screenshot():
    """Capture the ROI and return as bytes"""
    try:
        if SCREENSHOT_METHOD == "wsl_powershell":
            # WSL-specific method
            return wsl_powershell_screenshot(ROI)
        elif SCREENSHOT_METHOD == "pyautogui":
            # PyAutoGUI method
            img = pyautogui.screenshot(region=ROI)
        elif SCREENSHOT_METHOD == "mss":
            # MSS method
            with mss.mss() as sct:
                # Convert ROI format from (left, top, right, bottom) to (left, top, width, height)
                monitor = {"left": ROI[0], "top": ROI[1], 
                           "width": ROI[2] - ROI[0], "height": ROI[3] - ROI[1]}
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        elif SCREENSHOT_METHOD == "pillow":
            # PIL/Pillow method
            img = ImageGrab.grab(bbox=ROI)
        else:
            raise RuntimeError("No screenshot method available")

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    except Exception as e:
        print(f"Screenshot error: {e}")
        # Return a placeholder image or None
        img = Image.new('RGB', (300, 200), color=(73, 109, 137))
        d = ImageDraw.Draw(img)
        d.text((10, 10), f"Screenshot Error: {e}", fill=(255, 255, 0))
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

def has_roi_changed(new_screenshot):
    """Check if the ROI has changed significantly"""
    global last_screenshot
    
    if last_screenshot is None:
        return False
    
    try:
        # Convert bytes to images for comparison
        from PIL import Image
        img1 = Image.open(io.BytesIO(last_screenshot))
        img2 = Image.open(io.BytesIO(new_screenshot))
        
        # Convert to numpy arrays for comparison
        np1 = np.array(img1)
        np2 = np.array(img2)
        
        # Calculate mean absolute difference
        diff = np.mean(np.abs(np1 - np2))
        
        return diff > CHANGE_THRESHOLD
    except Exception as e:
        print(f"Error comparing screenshots: {e}")
        return False

def keyboard_listener():
    """Listen for keyboard events to trigger screenshots"""
    if not KEYBOARD_AVAILABLE:
        print("Keyboard shortcuts not available")
        return
        
    try:
        def on_trigger_key():
            try:
                new_screenshot = take_screenshot()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                screenshots.append((timestamp, new_screenshot))
                print(f"Key-triggered screenshot taken at {timestamp}")
            except Exception as e:
                print(f"Error in keyboard trigger: {e}")
        
        keyboard.add_hotkey(TRIGGER_KEY, on_trigger_key)
        print(f"Keyboard listener active. Press '{TRIGGER_KEY}' to take a screenshot.")
    except Exception as e:
        print(f"Failed to initialize keyboard listener: {e}")
        print("Keyboard shortcuts will not be available.")

def monitor_roi():
    """Monitor the ROI for changes and take screenshots as needed"""
    global last_screenshot
    
    print(f"Monitoring ROI {ROI}. Visit http://localhost:{PORT}/trigger for manual screenshot.")
    
    # Initial screenshot
    last_screenshot = take_screenshot()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    screenshots.append((timestamp, last_screenshot))
    print(f"Initial screenshot taken at {timestamp}")
    
    while True:
        time.sleep(CHECK_INTERVAL)
        
        # Take a new screenshot
        new_screenshot = take_screenshot()
        
        # Check if it's significantly different
        if has_roi_changed(new_screenshot):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            screenshots.append((timestamp, new_screenshot))
            last_screenshot = new_screenshot
            print(f"Change detected! Screenshot taken at {timestamp}")

def find_available_port(start_port, max_attempts):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            result = s.connect_ex(('localhost', port))
            if result != 0:  # Port is available
                return port
    raise OSError(f"Could not find an available port in range {start_port}-{start_port + max_attempts - 1}")

def main():
    global PORT
    
    # Find an available port
    try:
        PORT = find_available_port(PORT, MAX_PORT_ATTEMPTS)
        print(f"Using port {PORT}")
    except OSError as e:
        print(f"Error: {e}")
        return
    
    # Start the server
    handler = ScreenshotHandler
    httpd = socketserver.TCPServer(("", PORT), handler)
    
    print(f"Server started at http://localhost:{PORT}")
    
    # Start keyboard listener if available
    if KEYBOARD_AVAILABLE:
        keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
        keyboard_thread.start()
    
    # Start ROI monitoring in a separate thread
    monitor_thread = threading.Thread(target=monitor_roi, daemon=True)
    monitor_thread.start()
    
    # Run the server
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
        httpd.server_close()

if __name__ == "__main__":
    main()