// ScreenAgent UI JavaScript
class ScreenAgentUI {
    constructor() {
        this.currentTab = 'screenshots';
        this.screenshots = [];
        this.roi = null;
        this.isSelecting = false;
        this.selectionStart = null;
        this.selectionEnd = null;
        this.canvas = null;
        this.ctx = null;
        this.backgroundImage = null;
        this.isMonitoring = false;
        
        this.init();
    }
    
    init() {
        this.setupTabs();
        this.setupEventListeners();
        this.loadInitialData();
    }
    
    setupTabs() {
        const tabs = document.querySelectorAll('.nav-tab');
        const contents = document.querySelectorAll('.tab-content');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const targetTab = e.target.dataset.tab;
                this.switchTab(targetTab);
            });
        });
    }
    
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tabName).classList.add('active');
        
        this.currentTab = tabName;
        
        // Load tab-specific data
        if (tabName === 'settings') {
            this.loadSettings();
        } else if (tabName === 'monitor') {
            // Refresh ROI preview when switching to monitor tab
            setTimeout(() => this.updateRoiPreview(), 100);
        }
    }
    
    setupEventListeners() {
        // Screenshot actions
        const takeScreenshotBtn = document.getElementById('take-screenshot');
        if (takeScreenshotBtn) {
            takeScreenshotBtn.addEventListener('click', () => this.takeScreenshot());
        }
        
        const toggleMonitoringBtn = document.getElementById('toggle-monitoring');
        if (toggleMonitoringBtn) {
            toggleMonitoringBtn.addEventListener('click', () => this.toggleMonitoring());
        }
        
        const deleteAllBtn = document.getElementById('delete-all-screenshots');
        if (deleteAllBtn) {
            deleteAllBtn.addEventListener('click', () => this.deleteAllScreenshots());
        }
        
        const selectRoiBtn = document.getElementById('select-roi');
        if (selectRoiBtn) {
            selectRoiBtn.addEventListener('click', () => this.startRoiSelection());
        }
        
        const refreshPreviewBtn = document.getElementById('refresh-preview');
        if (refreshPreviewBtn) {
            refreshPreviewBtn.addEventListener('click', () => {
                console.log('Manual refresh preview triggered');
                this.loadRoiInfo();
                this.updateRoiPreview();
            });
        }
        
        // Make functions available for debugging
        window.debugROI = () => {
            console.log('Debug ROI - Current state:', {
                roi: this.roi,
                hasOverlay: !!document.getElementById('roi-overlay'),
                hasImage: !!document.getElementById('roi-preview-image')
            });
            const img = document.getElementById('roi-preview-image');
            if (img) {
                this.drawRoiOverlay(img);
            }
        };
        
        window.forceROI = () => {
            const overlay = document.getElementById('roi-overlay');
            if (overlay) {
                overlay.style.position = 'absolute';
                overlay.style.left = '10px';
                overlay.style.top = '10px';
                overlay.style.width = '200px';
                overlay.style.height = '150px';
                overlay.style.border = '4px solid #10b981';
                overlay.style.background = 'rgba(16, 185, 129, 0.5)';
                overlay.style.display = 'block';
                overlay.style.visibility = 'visible';
                overlay.style.zIndex = '999';
                console.log('Forced ROI overlay to be visible');
            }
        };
        
        // Settings form
        const settingsForm = document.getElementById('settings-form');
        if (settingsForm) {
            settingsForm.addEventListener('submit', (e) => this.saveSettings(e));
        }
        
        // Auto-refresh screenshots and ROI preview
        setInterval(() => {
            this.refreshScreenshots();
            this.loadMonitoringStatus(); // Check monitoring status regularly
            if (this.currentTab === 'monitor') {
                this.updateRoiPreview();
            }
        }, 30000); // Refresh every 30 seconds
    }
    
    async loadInitialData() {
        try {
            await this.refreshScreenshots();
            await this.loadRoiInfo();
            await this.loadMonitoringStatus();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showAlert('Error loading initial data', 'error');
        }
    }
    
    async refreshScreenshots() {
        try {
            const response = await fetch('/api/screenshots');
            const data = await response.json();
            
            if (data.success) {
                this.screenshots = data.screenshots;
                this.renderScreenshots();
                this.updateStatus(data.status);
            }
        } catch (error) {
            console.error('Error refreshing screenshots:', error);
        }
    }
    
    async loadRoiInfo() {
        try {
            console.log('Loading ROI info...');
            const response = await fetch('/api/roi');
            const data = await response.json();
            
            if (data.success) {
                this.roi = data.roi;
                console.log('ROI loaded successfully:', this.roi);
                this.updateRoiDisplay();
            } else {
                console.log('Failed to load ROI:', data);
            }
        } catch (error) {
            console.error('Error loading ROI info:', error);
        }
    }
    
    async loadMonitoringStatus() {
        try {
            console.log('Loading monitoring status...');
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (data.success) {
                this.isMonitoring = data.status.monitoring_active;
                this.updateMonitoringButton();
                console.log('Monitoring status loaded:', this.isMonitoring);
            } else {
                console.log('Failed to load monitoring status:', data);
            }
        } catch (error) {
            console.error('Error loading monitoring status:', error);
        }
    }
    
    updateMonitoringButton() {
        const button = document.getElementById('toggle-monitoring');
        if (button) {
            if (this.isMonitoring) {
                button.textContent = '⏹️ Stop Monitoring';
                button.className = 'btn btn-warning';
            } else {
                button.textContent = '🔍 Start Monitoring';
                button.className = 'btn btn-primary';
            }
        }
    }
    
    renderScreenshots() {
        const container = document.getElementById('screenshots-container');
        if (!container) return;
        
        if (this.screenshots.length === 0) {
            container.innerHTML = `
                <div class="text-center">
                    <p class="text-secondary">No screenshots captured yet.</p>
                    <button class="btn btn-primary mt-2" onclick="ui.takeScreenshot()">
                        Take First Screenshot
                    </button>
                </div>
            `;
            return;
        }
        
        const html = this.screenshots.map((screenshot, index) => `
            <div class="screenshot-item">
                <img src="/screenshot/${index}" 
                     alt="Screenshot ${index}" 
                     class="screenshot-image"
                     onclick="ui.viewScreenshot(${index})">
                <div class="screenshot-info">
                    <div class="screenshot-timestamp">${screenshot.timestamp}</div>
                    <div class="screenshot-actions">
                        <button class="btn btn-sm btn-primary" onclick="ui.viewScreenshot(${index})">
                            View
                        </button>
                        <button class="btn btn-sm btn-secondary" onclick="ui.analyzeScreenshot(${index})">
                            Analyze
                        </button>
                        <button class="btn btn-sm btn-outline" onclick="ui.downloadScreenshot(${index})">
                            Download
                        </button>
                    </div>
                    ${screenshot.llm_response ? `
                        <div class="llm-response mt-2">
                            <strong>AI Analysis:</strong><br>
                            ${screenshot.llm_response}
                        </div>
                    ` : ''}
                    <div id="llm-response-${index}" class="hidden"></div>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = html;
    }
    
    updateRoiDisplay() {
        const roiDisplay = document.getElementById('roi-display');
        if (roiDisplay && this.roi) {
            roiDisplay.textContent = `(${this.roi[0]}, ${this.roi[1]}, ${this.roi[2]}, ${this.roi[3]})`;
        }
        
        const roiPreview = document.getElementById('roi-preview');
        if (roiPreview) {
            this.updateRoiPreview();
        }
    }
    
    async updateRoiPreview() {
        try {
            console.log('updateRoiPreview called, current ROI:', this.roi);
            const response = await fetch('/api/preview');
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            
            const img = document.getElementById('roi-preview-image');
            if (img) {
                console.log('Setting image src and waiting for load...');
                img.onload = () => {
                    console.log('Image loaded, calling drawRoiOverlay');
                    setTimeout(() => {
                        this.drawRoiOverlay(img);
                    }, 100); // Small delay to ensure image is rendered
                    URL.revokeObjectURL(url);
                };
                img.src = url;
            } else {
                console.log('roi-preview-image element not found');
            }
        } catch (error) {
            console.error('Error updating ROI preview:', error);
        }
    }
    
    drawRoiOverlay(img) {
        console.log('drawRoiOverlay called');
        const overlay = document.getElementById('roi-overlay');
        if (!overlay) {
            console.log('ROI overlay element not found');
            return;
        }
        if (!this.roi) {
            console.log('No ROI data available');
            return;
        }
        
        console.log('Image properties:', {
            clientWidth: img.clientWidth,
            clientHeight: img.clientHeight,
            naturalWidth: img.naturalWidth,
            naturalHeight: img.naturalHeight
        });
        
        // Wait for image to be fully rendered
        if (img.naturalWidth === 0 || img.naturalHeight === 0) {
            console.log('Image not fully loaded, retrying...');
            setTimeout(() => this.drawRoiOverlay(img), 100);
            return;
        }
        
        const scaleX = img.clientWidth / img.naturalWidth;
        const scaleY = img.clientHeight / img.naturalHeight;
        
        const left = Math.max(0, this.roi[0] * scaleX);
        const top = Math.max(0, this.roi[1] * scaleY);
        const width = Math.max(10, (this.roi[2] - this.roi[0]) * scaleX);
        const height = Math.max(10, (this.roi[3] - this.roi[1]) * scaleY);
        
        overlay.style.left = left + 'px';
        overlay.style.top = top + 'px';
        overlay.style.width = width + 'px';
        overlay.style.height = height + 'px';
        overlay.style.display = 'block';
        overlay.style.visibility = 'visible';
        
        console.log('ROI overlay positioned:', {
            roi: this.roi,
            scale: { scaleX, scaleY },
            position: { left, top, width, height },
            overlayStyle: {
                left: overlay.style.left,
                top: overlay.style.top,
                width: overlay.style.width,
                height: overlay.style.height,
                display: overlay.style.display
            }
        });
    }
    
    updateStatus(status) {
        const statusEl = document.getElementById('status-indicator');
        if (!statusEl) return;
        
        statusEl.className = `status ${status.active ? 'status-active' : 'status-inactive'}`;
        statusEl.innerHTML = `
            <span class="status-dot"></span>
            ${status.active ? 'Monitoring' : 'Inactive'} 
            (${status.screenshot_count} screenshots)
        `;
    }
    
    async takeScreenshot() {
        const button = document.getElementById('take-screenshot');
        const originalText = button.textContent;
        
        try {
            button.disabled = true;
            button.innerHTML = '<span class="spinner"></span> Taking screenshot...';
            
            const response = await fetch('/api/trigger', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Screenshot captured successfully!', 'success');
                await this.refreshScreenshots();
            } else {
                this.showAlert(data.error || 'Failed to take screenshot', 'error');
            }
        } catch (error) {
            console.error('Error taking screenshot:', error);
            this.showAlert('Failed to take screenshot', 'error');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }
    
    async deleteAllScreenshots() {
        // Show confirmation dialog
        if (!confirm('Are you sure you want to delete all screenshots? This action cannot be undone.')) {
            return;
        }
        
        const button = document.getElementById('delete-all-screenshots');
        const originalText = button.textContent;
        
        try {
            button.disabled = true;
            button.innerHTML = '<span class="spinner"></span> Deleting...';
            
            const response = await fetch('/api/screenshots', { method: 'DELETE' });
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('All screenshots deleted successfully!', 'success');
                await this.refreshScreenshots();
            } else {
                this.showAlert(data.error || 'Failed to delete screenshots', 'error');
            }
        } catch (error) {
            console.error('Error deleting screenshots:', error);
            this.showAlert('Failed to delete screenshots', 'error');
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }
    
    async toggleMonitoring() {
        const button = document.getElementById('toggle-monitoring');
        const originalText = button.textContent;
        
        try {
            button.disabled = true;
            
            if (this.isMonitoring) {
                // Stop monitoring
                button.innerHTML = '<span class="spinner"></span> Stopping...';
                
                const response = await fetch('/api/monitoring/stop', { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    this.isMonitoring = false;
                    button.textContent = '🔍 Start Monitoring';
                    button.className = 'btn btn-primary';
                    this.showAlert('Monitoring stopped', 'info');
                } else {
                    this.showAlert(data.error || 'Failed to stop monitoring', 'error');
                }
            } else {
                // Start monitoring
                button.innerHTML = '<span class="spinner"></span> Starting...';
                
                const response = await fetch('/api/monitoring/start', { method: 'POST' });
                const data = await response.json();
                
                if (data.success) {
                    this.isMonitoring = true;
                    button.textContent = '⏹️ Stop Monitoring';
                    button.className = 'btn btn-warning';
                    this.showAlert('Monitoring started - screenshots will be taken automatically when changes are detected', 'success');
                } else {
                    this.showAlert(data.error || 'Failed to start monitoring', 'error');
                }
            }
        } catch (error) {
            console.error('Error toggling monitoring:', error);
            this.showAlert('Failed to toggle monitoring', 'error');
        } finally {
            button.disabled = false;
            if (button.innerHTML.includes('spinner')) {
                button.textContent = originalText;
            }
        }
    }
    
    async startRoiSelection() {
        try {
            window.location.href = '/select_roi';
        } catch (error) {
            console.error('Error starting ROI selection:', error);
            this.showAlert('Failed to start ROI selection', 'error');
        }
    }
    
    async analyzeScreenshot(index) {
        const responseEl = document.getElementById(`llm-response-${index}`);
        if (!responseEl) return;
        
        try {
            responseEl.classList.remove('hidden');
            responseEl.className = 'llm-response loading';
            responseEl.innerHTML = '<span class="spinner"></span> Analyzing image with AI...';
            
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ screenshot_idx: index })
            });
            
            const data = await response.json();
            
            if (data.success) {
                responseEl.className = 'llm-response';
                responseEl.innerHTML = `<strong>AI Analysis:</strong><br>${data.response}`;
                
                // Update the screenshot data
                this.screenshots[index].llm_response = data.response;
            } else {
                responseEl.className = 'llm-response error';
                responseEl.innerHTML = `<strong>Error:</strong> ${data.error}`;
            }
        } catch (error) {
            console.error('Error analyzing screenshot:', error);
            responseEl.className = 'llm-response error';
            responseEl.innerHTML = '<strong>Error:</strong> Failed to analyze image';
        }
    }
    
    viewScreenshot(index) {
        const screenshot = this.screenshots[index];
        if (!screenshot) return;
        
        // Create modal or new window to view full screenshot
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Screenshot - ${screenshot.timestamp}</h3>
                    <button class="btn btn-sm btn-outline" onclick="this.closest('.modal').remove()">
                        Close
                    </button>
                </div>
                <div class="modal-body">
                    <img src="/screenshot/${index}" alt="Screenshot ${index}" style="max-width: 100%; height: auto;">
                </div>
            </div>
        `;
        
        // Add modal styles if not already present
        if (!document.querySelector('style[data-modal]')) {
            const style = document.createElement('style');
            style.dataset.modal = 'true';
            style.textContent = `
                .modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.8);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    z-index: 1000;
                }
                .modal-content {
                    background: white;
                    border-radius: var(--border-radius);
                    max-width: 90vw;
                    max-height: 90vh;
                    overflow: auto;
                }
                .modal-header {
                    padding: 1rem;
                    border-bottom: 1px solid var(--border-color);
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .modal-body {
                    padding: 1rem;
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(modal);
        
        // Close modal on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
    
    downloadScreenshot(index) {
        const link = document.createElement('a');
        link.href = `/screenshot/${index}`;
        link.download = `screenshot-${this.screenshots[index].timestamp.replace(/[^a-zA-Z0-9]/g, '-')}.png`;
        link.click();
    }
    
    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            const data = await response.json();
            
            if (data.success) {
                const form = document.getElementById('settings-form');
                if (form) {
                    form.querySelector('#llm-enabled').checked = data.settings.enabled;
                    form.querySelector('#llm-model').value = data.settings.model || '';
                    form.querySelector('#llm-prompt').value = data.settings.prompt || '';
                }
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }
    
    async saveSettings(e) {
        e.preventDefault();
        
        const form = e.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        try {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner"></span> Saving...';
            
            const formData = new FormData(form);
            const settings = {
                enabled: formData.get('llm-enabled') === 'on',
                model: formData.get('llm-model'),
                prompt: formData.get('llm-prompt')
            };
            
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(settings)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('Settings saved successfully!', 'success');
            } else {
                this.showAlert(data.error || 'Failed to save settings', 'error');
            }
        } catch (error) {
            console.error('Error saving settings:', error);
            this.showAlert('Failed to save settings', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }
    
    showAlert(message, type = 'info') {
        // Remove any existing alerts
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.textContent = message;
        
        // Insert at the top of the main content
        const container = document.querySelector('.container');
        const header = container.querySelector('.header');
        container.insertBefore(alert, header.nextSibling);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }
}

// ROI Selection specific functionality
class ROISelector {
    constructor() {
        this.canvas = null;
        this.ctx = null;
        this.backgroundImage = null;
        this.isSelecting = false;
        this.startPoint = null;
        this.currentRoi = null;
        this.manualInputMode = false;
        
        this.init();
    }
    
    init() {
        console.log('ROISelector init - window.currentRoi:', window.currentRoi);
        this.canvas = document.getElementById('roi-canvas');
        if (!this.canvas) return;
        
        this.ctx = this.canvas.getContext('2d');
        this.setupEventListeners();
        this.loadBackgroundImage();
        this.setupManualInput();
    }
    
    setupEventListeners() {
        this.canvas.addEventListener('mousedown', (e) => this.startSelection(e));
        this.canvas.addEventListener('mousemove', (e) => this.updateSelection(e));
        this.canvas.addEventListener('mouseup', (e) => this.endSelection(e));
        this.canvas.addEventListener('mouseleave', (e) => this.endSelection(e));
        
        const setRoiBtn = document.getElementById('set-roi-btn');
        if (setRoiBtn) {
            setRoiBtn.addEventListener('click', () => this.setRoi());
        }
    }
    
    setupManualInput() {
        // Toggle manual input section
        const toggleBtn = document.getElementById('toggle-manual-input');
        const manualSection = document.getElementById('manual-input-section');
        
        if (toggleBtn && manualSection) {
            toggleBtn.addEventListener('click', () => {
                const isHidden = manualSection.classList.contains('hidden');
                manualSection.classList.toggle('hidden');
                toggleBtn.textContent = isHidden ? 'Hide Manual Input' : 'Show Manual Input';
            });
        }
        
        // Manual input controls
        const applyBtn = document.getElementById('apply-manual-roi');
        const clearBtn = document.getElementById('clear-manual-roi');
        const loadBtn = document.getElementById('load-current-roi');
        
        if (applyBtn) {
            applyBtn.addEventListener('click', () => this.applyManualRoi());
        }
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearManualInputs());
        }
        
        if (loadBtn) {
            loadBtn.addEventListener('click', () => this.loadCurrentRoiToInputs());
        }
        
        // Add input event listeners for real-time validation
        const inputs = ['roi-left', 'roi-top', 'roi-right', 'roi-bottom'];
        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', () => this.updateDimensionsFromInputs());
                input.addEventListener('change', () => this.validateManualInputs());
            }
        });
        
        // Initialize with current ROI if available
        if (window.currentRoi) {
            this.loadCurrentRoiToInputs();
        }
    }
    
    async loadBackgroundImage() {
        try {
            console.log('Starting to load background image...');
            const img = new Image();
            const imageUrl = '/temp_screenshot?' + Date.now();
            console.log('Image URL:', imageUrl);
            
            img.onload = () => {
                console.log('Image loaded successfully:', img.width, 'x', img.height);
                this.backgroundImage = img;
                
                // Calculate appropriate canvas size to fit in container
                const container = this.canvas.parentElement;
                const maxWidth = container.clientWidth - 32; // Account for padding
                const maxHeight = Math.min(window.innerHeight * 0.6, 600); // Reduced height limit
                
                let canvasWidth = img.width;
                let canvasHeight = img.height;
                
                // Scale down if image is too large
                const scaleX = maxWidth / img.width;
                const scaleY = maxHeight / img.height;
                const scale = Math.min(scaleX, scaleY, 1); // Don't scale up, only down
                
                if (scale < 1) {
                    canvasWidth = img.width * scale;
                    canvasHeight = img.height * scale;
                }
                
                this.canvas.width = canvasWidth;
                this.canvas.height = canvasHeight;
                this.canvas.style.width = canvasWidth + 'px';
                this.canvas.style.height = canvasHeight + 'px';
                
                // Store the scale factor for coordinate conversion
                this.imageScale = scale;
                this.originalImageWidth = img.width;
                this.originalImageHeight = img.height;
                
                this.redraw();
                
                // Ensure the canvas container is scrolled to show the top
                setTimeout(() => {
                    const container = this.canvas.parentElement;
                    if (container) {
                        container.scrollTop = 0;
                        container.scrollLeft = 0;
                    }
                }, 100);
            };
            
            img.onerror = (e) => {
                console.error('Failed to load background image:', e);
                console.error('Image src:', img.src);
                const errorEl = document.getElementById('error-message');
                if (errorEl) {
                    errorEl.textContent = 'Failed to capture screenshot. The image could not be loaded from the server.';
                    errorEl.classList.remove('hidden');
                    errorEl.style.display = 'block';
                }
            };
            
            img.src = imageUrl;
        } catch (error) {
            console.error('Error in loadBackgroundImage:', error);
        }
    }
    
    startSelection(e) {
        const rect = this.canvas.getBoundingClientRect();
        this.startPoint = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        this.isSelecting = true;
    }
    
    updateSelection(e) {
        if (!this.isSelecting) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const currentPoint = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        
        const canvasRoi = [
            Math.min(this.startPoint.x, currentPoint.x),
            Math.min(this.startPoint.y, currentPoint.y),
            Math.max(this.startPoint.x, currentPoint.x),
            Math.max(this.startPoint.y, currentPoint.y)
        ];
        
        this.redraw();
        this.drawRoi(canvasRoi);
        
        // Update display with original image coordinates
        const originalRoi = this.scaleRoiToOriginal(canvasRoi);
        this.updateRoiDisplay(originalRoi);
    }
    
    endSelection(e) {
        if (!this.isSelecting) return;
        
        this.isSelecting = false;
        
        const rect = this.canvas.getBoundingClientRect();
        const endPoint = {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
        
        const canvasRoi = [
            Math.min(this.startPoint.x, endPoint.x),
            Math.min(this.startPoint.y, endPoint.y),
            Math.max(this.startPoint.x, endPoint.x),
            Math.max(this.startPoint.y, endPoint.y)
        ];
        
        // Convert canvas coordinates to original image coordinates
        this.currentRoi = this.scaleRoiToOriginal(canvasRoi);
        
        this.validateRoi();
    }
    
    redraw() {
        if (!this.backgroundImage) return;
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw the scaled image
        this.ctx.drawImage(
            this.backgroundImage, 
            0, 0, 
            this.canvas.width, 
            this.canvas.height
        );
        
        // Draw current ROI if available
        if (window.currentRoi && Array.isArray(window.currentRoi) && window.currentRoi.length === 4) {
            console.log('Drawing current ROI:', window.currentRoi);
            this.drawRoi(this.scaleRoiToCanvas(window.currentRoi), true);
        } else {
            console.log('No current ROI to draw or invalid format:', window.currentRoi);
        }
    }
    
    // Helper methods for coordinate conversion
    scaleRoiToCanvas(roi) {
        if (!this.imageScale) return roi;
        const [left, top, right, bottom] = roi;
        return [
            left * this.imageScale,
            top * this.imageScale,
            right * this.imageScale,
            bottom * this.imageScale
        ];
    }
    
    scaleRoiToOriginal(roi) {
        if (!this.imageScale) return roi;
        const [left, top, right, bottom] = roi;
        return [
            Math.round(left / this.imageScale),
            Math.round(top / this.imageScale),
            Math.round(right / this.imageScale),
            Math.round(bottom / this.imageScale)
        ];
    }
    
    drawRoi(roi, isInitial = false) {
        const [left, top, right, bottom] = roi;
        
        // Draw rectangle outline
        this.ctx.strokeStyle = isInitial ? '#10b981' : '#ef4444';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(left, top, right - left, bottom - top);
        
        // Draw semi-transparent fill
        this.ctx.fillStyle = isInitial ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)';
        this.ctx.fillRect(left, top, right - left, bottom - top);
    }
    
    updateRoiDisplay(roi) {
        const display = document.getElementById('roi-display');
        if (display) {
            display.textContent = `(${Math.round(roi[0])}, ${Math.round(roi[1])}, ${Math.round(roi[2])}, ${Math.round(roi[3])})`;
        }
    }
    
    validateRoi() {
        if (!this.currentRoi) return;
        
        const [left, top, right, bottom] = this.currentRoi;
        const errorEl = document.getElementById('error-message');
        const setBtn = document.getElementById('set-roi-btn');
        
        if (right <= left || bottom <= top) {
            errorEl.textContent = 'Invalid selection: width and height must be positive.';
            setBtn.disabled = true;
            return;
        }
        
        if (right - left < 10 || bottom - top < 10) {
            errorEl.textContent = 'Selection too small: must be at least 10x10 pixels.';
            setBtn.disabled = true;
            return;
        }
        
        errorEl.textContent = '';
        setBtn.disabled = false;
    }
    
    async setRoi() {
        if (!this.currentRoi) return;
        
        const button = document.getElementById('set-roi-btn');
        const originalText = button.textContent;
        
        try {
            button.disabled = true;
            button.innerHTML = '<span class="spinner"></span> Setting ROI...';
            
            const response = await fetch('/set_roi', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ roi: this.currentRoi })
            });
            
            const data = await response.json();
            
            if (data.success) {
                window.location.href = '/';
            } else {
                document.getElementById('error-message').textContent = data.error || 'Failed to set ROI';
            }
        } catch (error) {
            console.error('Error setting ROI:', error);
            document.getElementById('error-message').textContent = 'Error: ' + error.message;
        } finally {
            button.disabled = false;
            button.textContent = originalText;
        }
    }
    
    // Manual input methods
    applyManualRoi() {
        const left = parseInt(document.getElementById('roi-left').value) || 0;
        const top = parseInt(document.getElementById('roi-top').value) || 0;
        const right = parseInt(document.getElementById('roi-right').value) || 0;
        const bottom = parseInt(document.getElementById('roi-bottom').value) || 0;
        
        const originalRoi = [left, top, right, bottom];
        
        // Validate the ROI
        if (this.isValidRoi(originalRoi)) {
            this.currentRoi = originalRoi;
            this.redraw(); // This will draw the current ROI automatically
            this.updateRoiDisplay(originalRoi);
            this.validateRoi();
            
            // Clear any error messages
            const errorEl = document.getElementById('error-message');
            if (errorEl) errorEl.textContent = '';
        }
    }
    
    clearManualInputs() {
        const inputs = ['roi-left', 'roi-top', 'roi-right', 'roi-bottom', 'roi-width', 'roi-height'];
        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) input.value = '';
        });
        
        this.currentRoi = null;
        this.redraw();
        
        // Draw current ROI if available
        if (window.currentRoi) {
            const canvasRoi = this.scaleRoiToCanvas(window.currentRoi);
            this.drawRoi(canvasRoi, true);
        }
        
        const setBtn = document.getElementById('set-roi-btn');
        if (setBtn) setBtn.disabled = true;
    }
    
    loadCurrentRoiToInputs() {
        const roi = window.currentRoi;
        if (roi && Array.isArray(roi) && roi.length === 4) {
            document.getElementById('roi-left').value = roi[0];
            document.getElementById('roi-top').value = roi[1];
            document.getElementById('roi-right').value = roi[2];
            document.getElementById('roi-bottom').value = roi[3];
            this.updateDimensionsFromInputs();
        }
    }
    
    updateDimensionsFromInputs() {
        const left = parseInt(document.getElementById('roi-left').value) || 0;
        const top = parseInt(document.getElementById('roi-top').value) || 0;
        const right = parseInt(document.getElementById('roi-right').value) || 0;
        const bottom = parseInt(document.getElementById('roi-bottom').value) || 0;
        
        const width = Math.max(0, right - left);
        const height = Math.max(0, bottom - top);
        
        document.getElementById('roi-width').value = width;
        document.getElementById('roi-height').value = height;
    }
    
    validateManualInputs() {
        const left = parseInt(document.getElementById('roi-left').value) || 0;
        const top = parseInt(document.getElementById('roi-top').value) || 0;
        const right = parseInt(document.getElementById('roi-right').value) || 0;
        const bottom = parseInt(document.getElementById('roi-bottom').value) || 0;
        
        const roi = [left, top, right, bottom];
        const errorEl = document.getElementById('error-message');
        const applyBtn = document.getElementById('apply-manual-roi');
        
        if (!this.isValidRoi(roi)) {
            errorEl.textContent = 'Invalid coordinates: ensure right > left, bottom > top, and size ≥ 10x10 pixels';
            if (applyBtn) applyBtn.disabled = true;
        } else {
            errorEl.textContent = '';
            if (applyBtn) applyBtn.disabled = false;
        }
    }
    
    isValidRoi(roi) {
        const [left, top, right, bottom] = roi;
        
        // Check if all values are valid numbers
        if (roi.some(val => isNaN(val) || val < 0)) return false;
        
        // Check if dimensions are valid
        if (right <= left || bottom <= top) return false;
        
        // Check minimum size
        if (right - left < 10 || bottom - top < 10) return false;
        
        return true;
    }
}

// Initialize the appropriate UI class based on the page
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('roi-canvas')) {
        window.roiSelector = new ROISelector();
    } else {
        window.ui = new ScreenAgentUI();
    }
});
