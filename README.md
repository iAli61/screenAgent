# ScreenAgent 🎯

A modern, intelligent screen monitoring application that captures and analyzes changes within user-defined regions of interest (ROI) using AI-powered analysis.

## ✨ Key Features

- **🎯 Smart ROI Monitoring**: Interactive region selection with real-time change detection
- **🤖 AI-Powered Analysis**: Multi-provider AI integration (OpenAI GPT-4 Vision, Azure AI)
- **🌐 Modern Web Interface**: Responsive dashboard with real-time updates and screenshot gallery
- **📱 Cross-Platform**: Seamless operation on Linux, Windows, and WSL environments
- **⚙️ Flexible Configuration**: Web-based settings with dynamic updates
- **⌨️ Keyboard Shortcuts**: Global hotkeys for manual screenshot capture
- **� Real-time Statistics**: Monitor uptime, capture count, and system performance

> 📋 **For comprehensive feature details, system architecture, and design documentation, see [Design.md](./Design.md)**

## 🚀 Quick Start

### Prerequisites
- Python 3.7+ with pip
- Internet connection (for AI features)
- Display server (X11/Wayland on Linux, native on Windows/WSL)

### Installation

1. **Clone and setup:**
   ```bash
   git clone https://github.com/your-username/screenAgent.git
   cd screenAgent
   pip install -r requirements.txt
   ```

2. **Configure AI (optional):**
   ```bash
   # Create .env file or set environment variables
   export OPENAI_API_KEY="your-openai-api-key"
   # OR
   export AZURE_AI_ENDPOINT="your-azure-endpoint"
   export AZURE_AI_API_KEY="your-azure-api-key"
   ```

3. **Start ScreenAgent:**
   ```bash
   python main.py
   ```

4. **Open browser:** Navigate to `http://localhost:8000`

### Basic Usage

1. **Select ROI**: Click "Select New ROI" to define your monitoring area
2. **Configure Settings**: Adjust sensitivity and monitoring interval
3. **Start Monitoring**: Click "Start Monitoring" to begin automatic capture
4. **View Results**: Browse screenshots in the gallery with AI analysis

## 🎨 Web Interface Overview

### 📊 Dashboard
- **Status Panel**: Real-time monitoring indicators and system statistics
- **Quick Actions**: Start/stop monitoring, manual screenshot capture
- **ROI Preview**: Visual feedback of current monitoring region

### 🖼️ Screenshot Gallery
- **Grid Layout**: Organized thumbnails with timestamps and metadata
- **AI Integration**: One-click analysis with custom prompts
- **Management**: View, download, or delete individual/all screenshots

### ⚙️ Settings
- **Monitoring**: Sensitivity, interval, and threshold configuration
- **AI Options**: Provider selection, model choice, custom prompts
- **Preferences**: Auto-start, keyboard shortcuts, display options

## 🔧 Configuration Options

| Setting | Description | Default | Example |
|---------|-------------|---------|---------|
| `roi` | Monitoring region coordinates | `[100, 100, 800, 800]` | `[0, 0, 1920, 1080]` |
| `change_threshold` | Change detection sensitivity | `20` | `10` (more sensitive) |
| `check_interval` | Monitoring frequency (seconds) | `0.5` | `1.0` (less frequent) |
| `llm_enabled` | Enable AI analysis | `false` | `true` |
| `llm_model` | AI model selection | `gpt-4o` | `gpt-4-vision-preview` |
| `max_screenshots` | Screenshot retention limit | `100` | `500` |

> 🔧 **For complete configuration details and advanced options, see [Design.md](./Design.md#configuration-system)**

## 🏗️ Project Structure

```
screenAgent/
├── main.py                    # Application entry point
├── src/                       # Source code modules
│   ├── core/                  # Core functionality
│   │   ├── config.py          # Configuration management
│   │   ├── screenshot_manager.py  # Screenshot coordination
│   │   ├── screenshot_capture.py  # Platform-specific capture
│   │   ├── roi_monitor.py     # Change detection engine
│   │   ├── keyboard_handler.py    # Global hotkey support
│   │   └── platform_detection.py  # OS/environment detection
│   └── api/                   # Web server and AI integration
│       ├── server.py          # HTTP server and REST API
│       └── llm_api.py         # Multi-provider AI analysis
├── static/                    # Web assets
│   ├── css/style.css         # Modern responsive CSS
│   └── js/app.js             # Interactive frontend
├── templates/                 # HTML templates
│   ├── index.html            # Main dashboard
│   └── select_roi.html       # ROI selection interface
└── requirements.txt          # Python dependencies
```

> 🏗️ **For detailed architecture and design patterns, see [Design.md](./Design.md#architecture)**

## 🤖 AI Analysis

ScreenAgent supports multiple AI providers for intelligent screenshot analysis:

- **OpenAI**: GPT-4 Vision, GPT-4o for visual understanding
- **Azure AI**: Azure OpenAI Service integration
- **Custom Prompts**: Configurable analysis prompts for specific use cases

**AI Capabilities:**
- Content description and change detection
- Text extraction and UI element identification  
- Anomaly detection and automated insights
- Contextual analysis of screen activities

> 🤖 **For complete AI integration details and configuration, see [Design.md](./Design.md#ai-integration)**

## �️ Platform Support

| Platform | Capture Method | Keyboard | Notes |
|----------|---------------|----------|-------|
| **Linux** | PIL/MSS/PyAutoGUI | Root required | Native X11/Wayland |
| **Windows** | PIL/PyAutoGUI | Native support | Windows API integration |
| **WSL** | PowerShell bridge | Host dependent | Full functionality |

> 🖥️ **For platform-specific details and troubleshooting, see [Design.md](./Design.md#platform-support)**

## 🛠️ Development & Contributing

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/screenAgent.git
cd screenAgent

# Install development dependencies
pip install -r requirements.txt

# Run tests
python test_basic.py

# Start development server
python main.py
```

### Testing
- `test_basic.py` - Core functionality tests
- `test_comprehensive_screenshot.py` - Screenshot capture tests
- `test_roi_functionality.py` - ROI monitoring tests
- `minimal_test.py` - Minimal example

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with tests
4. Submit a pull request

> 🛠️ **For detailed development guidelines and architecture, see [Design.md](./Design.md)**

## 🐛 Troubleshooting

### Common Issues

**No screenshots captured:**
- Verify permissions (Linux: may need `sudo`, WSL: check Windows display)
- Check ROI coordinates are within screen bounds
- Ensure display server is running (`$DISPLAY` on Linux)

**AI analysis not working:**
- Verify API keys: `echo $OPENAI_API_KEY` or `echo $AZURE_AI_API_KEY`
- Check internet connection and provider status
- Review console logs for API errors

**Web interface not accessible:**
- Check if port 8000 is available: `netstat -tulpn | grep 8000`
- Try different port: Set `PORT=8080` environment variable
- Verify firewall/security settings

**Performance issues:**
- Reduce monitoring frequency (increase `check_interval`)
- Lower change sensitivity (increase `change_threshold`)
- Install `mss` for faster screenshots: `pip install mss`

> 🐛 **For comprehensive troubleshooting and error handling, see [Design.md](./Design.md#error-handling--reliability)**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AI Integration**: OpenAI GPT-4 Vision and Azure AI Services
- **Screenshot Libraries**: PIL, PyAutoGUI, MSS for cross-platform support
- **Modern Web**: Vanilla JavaScript and CSS Grid for responsive design
- **Platform Detection**: Advanced WSL and display server detection

---

**📋 For comprehensive documentation, see [Design.md](./Design.md) - your single source of truth for system architecture, features, and implementation details.**