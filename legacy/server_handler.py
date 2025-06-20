import http.server
import socketserver
import json
import os
from datetime import datetime
from PIL import Image
import io

from config import save_to_config, TEMP_SCREENSHOT_PATH, load_from_config, DEFAULT_LLM_ENABLED, DEFAULT_LLM_MODEL, DEFAULT_LLM_PROMPT
from screenshot import take_full_screenshot, take_screenshot
from llm_handler import llm_handler

class ScreenshotHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for the screenshot server"""
    
    # Class variable to store screenshots
    screenshots = []
    # Reference to the current ROI settings
    roi = (100, 100, 400, 400)
    # Store LLM responses
    llm_responses = {}
    
    @classmethod
    def set_roi(cls, roi):
        """Set the ROI for all handler instances"""
        cls.roi = roi
    
    @classmethod
    def add_screenshot(cls, timestamp, screenshot):
        """Add a screenshot to the collection"""
        cls.screenshots.append((timestamp, screenshot))
    
    # Helper to parse JSON from POST requests
    def parse_json_body(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        return json.loads(post_data.decode('utf-8'))
    
    def send_json_response(self, data, status=200):
        """Send a JSON response with given status code"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/set_roi':
            self.handle_set_roi()
        elif self.path == '/analyze_image':
            self.handle_analyze_image()
        elif self.path == '/save_llm_settings':
            self.handle_save_llm_settings()
        else:
            self.send_response(404)
            self.end_headers()
    
    def handle_set_roi(self):
        """Handle ROI setting POST request"""
        try:
            roi_data = self.parse_json_body()
            
            # Validate ROI data
            if 'roi' in roi_data and len(roi_data['roi']) == 4:
                left, top, right, bottom = map(int, roi_data['roi'])
                
                # Validate the ROI dimensions
                if left < right and top < bottom and right - left > 10 and bottom - top > 10:
                    self.roi = (left, top, right, bottom)
                    self.__class__.set_roi(self.roi)
                    save_to_config('roi', self.roi)
                    print(f"ROI updated to {self.roi}")
                    
                    # Send success response
                    self.send_json_response({'success': True, 'roi': self.roi})
                    
                    # Clean up the temporary screenshot
                    self.delete_temp_screenshot()
                    return
            
            # If we get here, something was wrong with the ROI data
            self.send_json_response({'success': False, 'error': 'Invalid ROI'}, status=400)
            
        except Exception as e:
            print(f"Error processing ROI POST data: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, status=400)

    def handle_analyze_image(self):
        """Handle LLM analysis of an image"""
        try:
            data = self.parse_json_body()
            screenshot_idx = int(data.get('screenshot_idx', -1))
            custom_prompt = data.get('prompt', None)
            
            # Check if index is valid
            if 0 <= screenshot_idx < len(self.screenshots):
                # Get the screenshot
                timestamp, screenshot_bytes = self.screenshots[screenshot_idx]
                
                # Analyze the image with LLM
                result = llm_handler.analyze_image(screenshot_bytes, custom_prompt)
                
                # Store the response
                if result['success']:
                    self.__class__.llm_responses[screenshot_idx] = result['response']
                else:
                    self.__class__.llm_responses[screenshot_idx] = "Error: " + result['error']
                # Print the result for debugging
                print(f"LLM analysis result for screenshot {screenshot_idx}: {result}")
                
                # Return the result
                self.send_json_response(result)
            else:
                self.send_json_response({'success': False, 'error': 'Invalid screenshot index'}, status=400)
                
        except Exception as e:
            print(f"Error processing analyze image request: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, status=400)
    
    def handle_save_llm_settings(self):
        """Handle saving LLM settings"""
        try:
            settings = self.parse_json_body()
            
            # Update settings
            enabled = settings.get('enabled', DEFAULT_LLM_ENABLED)
            model = settings.get('model', DEFAULT_LLM_MODEL)
            prompt = settings.get('prompt', DEFAULT_LLM_PROMPT)
            
            # Save to config
            save_to_config('llm_enabled', enabled)
            save_to_config('llm_model', model)
            save_to_config('llm_prompt', prompt)
            
            # Reload the LLM handler
            llm_handler.enabled = enabled
            llm_handler.model = model
            llm_handler.prompt = prompt
            
            self.send_json_response({'success': True})
            
        except Exception as e:
            print(f"Error saving LLM settings: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, status=400)
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_main_page()
        elif self.path == '/trigger':
            self.handle_trigger()
        elif self.path == '/select_roi':
            self.handle_select_roi()
        elif self.path.startswith('/temp_screenshot'):
            self.serve_temp_screenshot()
        elif self.path.startswith('/screenshot/'):
            self.serve_screenshot()
        elif self.path == '/llm_settings':
            self.handle_llm_settings()
        elif self.path.startswith('/set_roi'):
            # Redirect to the ROI selection page
            self.send_response(302)
            self.send_header('Location', '/select_roi')
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()
    
    def serve_main_page(self):
        """Serve the main HTML page"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Get the latest screenshot for the ROI preview
        latest_screenshot = None
        latest_screenshot_idx = -1
        if self.screenshots:
            latest_screenshot_idx = len(self.screenshots) - 1
            latest_screenshot = self.screenshots[latest_screenshot_idx][1]
        
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
                .llm-response {
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 10px;
                    margin-top: 10px;
                    background-color: #f9f9f9;
                    white-space: pre-wrap;
                }
                .tabs {
                    display: flex;
                    margin-bottom: 10px;
                }
                .tab {
                    padding: 10px 15px;
                    cursor: pointer;
                    border: 1px solid #ddd;
                    border-radius: 4px 4px 0 0;
                    background-color: #f1f1f1;
                    margin-right: 5px;
                }
                .tab.active {
                    background-color: white;
                    border-bottom: 1px solid white;
                }
                .tab-content {
                    display: none;
                    border: 1px solid #ddd;
                    padding: 15px;
                    border-radius: 0 0 4px 4px;
                }
                .tab-content.active {
                    display: block;
                }
                .loading {
                    color: #666;
                    font-style: italic;
                }
            </style>
        </head>
        <body>
            <h1>ROI Screenshot Server</h1>
            
            <div class="tabs">
                <div class="tab active" onclick="openTab(event, 'screenshots')">Screenshots</div>
                <div class="tab" onclick="openTab(event, 'settings')">LLM Settings</div>
            </div>
            
            <div id="screenshots" class="tab-content active">
                <p>Monitoring ROI: """ + str(self.roi) + """</p>
                
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
                            const roi = {self.roi};
                            
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
                </div>
                
                <h2>Screenshots</h2>
                <div class="screenshot-list">
        """
        
        # LLM functionality enabled check
        llm_enabled = load_from_config('llm_enabled', DEFAULT_LLM_ENABLED)
        
        # List screenshots
        for i, (timestamp, _) in enumerate(self.screenshots):
            html += f'<div class="screenshot-entry">'
            html += f'<h3><a href="/screenshot/{i}">{timestamp}</a></h3>'
            
            # Add LLM analysis button if enabled
            if llm_enabled:
                html += f'<button class="button" onclick="analyzeImage({i})">Analyze with LLM</button>'
                
                # Show LLM response if available
                if i in self.llm_responses:
                    html += f'<div class="llm-response">{self.llm_responses[i]}</div>'
                else:
                    html += f'<div id="llm-response-{i}" class="llm-response" style="display: none;"></div>'
            
            html += '</div>'
        
        html += """
            </div>
            </div>
            
            <div id="settings" class="tab-content">
                <h2>LLM Integration Settings</h2>
                <form id="llm-settings-form">
                    <p>
                        <label>
                            <input type="checkbox" id="llm-enabled" name="llm-enabled" """ + ("checked" if llm_enabled else "") + """> 
                            Enable LLM Analysis
                        </label>
                    </p>
                    <p>
                        <label for="llm-model">LLM Model:</label><br>
                        <input type="text" id="llm-model" name="llm-model" value=\"""" + load_from_config('llm_model', DEFAULT_LLM_MODEL) + """\" style="width: 100%;">
                    </p>
                    <p>
                        <label for="llm-prompt">Default Prompt:</label><br>
                        <textarea id="llm-prompt" name="llm-prompt" rows="3" style="width: 100%;">""" + load_from_config('llm_prompt', DEFAULT_LLM_PROMPT) + """</textarea>
                    </p>
                    <button type="submit" class="button">Save Settings</button>
                </form>
                <p id="settings-result"></p>
            </div>
            
            <script>
                // Tab functionality
                function openTab(evt, tabName) {
                    var i, tabcontent, tablinks;
                    tabcontent = document.getElementsByClassName("tab-content");
                    for (i = 0; i < tabcontent.length; i++) {
                        tabcontent[i].className = tabcontent[i].className.replace(" active", "");
                    }
                    tablinks = document.getElementsByClassName("tab");
                    for (i = 0; i < tablinks.length; i++) {
                        tablinks[i].className = tablinks[i].className.replace(" active", "");
                    }
                    document.getElementById(tabName).className += " active";
                    evt.currentTarget.className += " active";
                }
                
                // LLM analysis function
                function analyzeImage(idx) {
                    const responseEl = document.getElementById(`llm-response-${idx}`) || 
                                    document.querySelector(`.screenshot-entry:nth-child(${idx + 1}) .llm-response`);
                    
                    if (responseEl) {
                        responseEl.style.display = 'block';
                        responseEl.innerHTML = '<p class="loading">Analyzing image with LLM, please wait...</p>';
                        
                        fetch('/analyze_image', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({ screenshot_idx: idx })
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                responseEl.innerHTML = data.response;
                            } else {
                                responseEl.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                            }
                        })
                        .catch(error => {
                            responseEl.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
                        });
                    }
                }
                
                // LLM settings form handling
                document.getElementById('llm-settings-form').addEventListener('submit', function(e) {
                    e.preventDefault();
                    const enabled = document.getElementById('llm-enabled').checked;
                    const model = document.getElementById('llm-model').value;
                    const prompt = document.getElementById('llm-prompt').value;
                    
                    const resultEl = document.getElementById('settings-result');
                    resultEl.innerHTML = '<p class="loading">Saving settings...</p>';
                    
                    fetch('/save_llm_settings', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ enabled, model, prompt })
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            resultEl.innerHTML = '<p style="color: green;">Settings saved successfully!</p>';
                            setTimeout(() => { resultEl.innerHTML = ''; }, 3000);
                        } else {
                            resultEl.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
                        }
                    })
                    .catch(error => {
                        resultEl.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
                    });
                });
            </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def handle_llm_settings(self):
        """Handle LLM settings page"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        settings = {
            'enabled': load_from_config('llm_enabled', DEFAULT_LLM_ENABLED),
            'model': load_from_config('llm_model', DEFAULT_LLM_MODEL),
            'prompt': load_from_config('llm_prompt', DEFAULT_LLM_PROMPT)
        }
        
        self.wfile.write(json.dumps(settings).encode())
    
    def handle_trigger(self):
        """Handle manual screenshot trigger request"""
        new_screenshot = take_screenshot(self.roi)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.__class__.add_screenshot(timestamp, new_screenshot)
        print(f"Manual screenshot taken at {timestamp}")
        
        # Redirect back to homepage
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()
    
    def serve_temp_screenshot(self):
        """Serve the temporary screenshot for ROI selection"""
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
    
    def serve_screenshot(self):
        """Serve a specific screenshot by index"""
        try:
            idx = int(self.path.split('/')[-1])
            if 0 <= idx < len(self.screenshots):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                self.wfile.write(self.screenshots[idx][1])
            else:
                self.send_response(404)
                self.end_headers()
        except:
            self.send_response(404)
            self.end_headers()
    
    def store_temp_screenshot(self, screenshot_bytes):
        """Store a temporary screenshot for ROI selection"""
        try:
            with open(TEMP_SCREENSHOT_PATH, 'wb') as f:
                f.write(screenshot_bytes)
            return True
        except Exception as e:
            print(f"Error storing temporary screenshot: {e}")
            return False

    def delete_temp_screenshot(self):
        """Delete the temporary screenshot file if it exists"""
        if os.path.exists(TEMP_SCREENSHOT_PATH):
            try:
                os.remove(TEMP_SCREENSHOT_PATH)
                return True
            except Exception as e:
                print(f"Error deleting temporary screenshot: {e}")
        return False

    def handle_select_roi(self):
        """Handle ROI selection page request"""
        # Take a full-screen screenshot for the background and save it to the temp file
        # The save_to_temp=True parameter will ensure the file isn't deleted after capturing
        full_screenshot = take_full_screenshot(save_to_temp=True)
        
        # No need to explicitly store the screenshot since take_full_screenshot now does it
        # when save_to_temp=True
        
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
                <p>Current ROI: <span id="roi-display">""" + str(self.roi) + """</span></p>
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
                
                // Load the screenshot image with cache-busting query parameter
                const img = new Image();
                img.src = '/temp_screenshot?' + new Date().getTime(); 
                
                img.onload = function() {
                    console.log("Screenshot loaded, dimensions:", img.width, "x", img.height);
                    // Set canvas size to match image
                    canvas.width = img.width;
                    canvas.height = img.height;
                    
                    // Draw the image initially
                    ctx.drawImage(img, 0, 0);
                    
                    // Draw initial ROI if available
                    const initialRoi = """ + str(self.roi) + """;
                    drawRectangle(initialRoi[0], initialRoi[1], initialRoi[2], initialRoi[3], true);
                };
                
                img.onerror = function() {
                    console.error("Failed to load screenshot");
                    errorMessage.textContent = "Failed to load screenshot. Please try again.";
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