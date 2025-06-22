# ScreenAgent 🎯

A modern, intelligent screen monitoring application that captures and analyzes changes within user-defined regions of interest (ROI) using AI-powered analysis. Built with a modular, event-driven architecture for enhanced maintainability and extensibility.

## ✨ Key Features

- **🎯 Smart ROI Monitoring**: Interactive region selection with real-time change detection
- **🤖 AI-Powered Analysis**: Multi-provider AI integration (OpenAI GPT-4 Vision, Azure AI)
- **🌐 Modern Web Interface**: Responsive dashboard with real-time updates and screenshot gallery
- **📱 Cross-Platform**: Seamless operation on Linux, Windows, and WSL environments
- **⚙️ Flexible Configuration**: Web-based settings with dynamic updates
- **⌨️ Keyboard Shortcuts**: Global hotkeys for manual screenshot capture
- **📊 Real-time Statistics**: Monitor uptime, capture count, and system performance
- **🏗️ Modular Architecture**: Event-driven design with pluggable storage and capture backends 🎯

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
| `storage_type` | Storage backend type | `filesystem` | `memory` |
| `screenshot_dir` | Screenshot storage directory | `screenshots/` | `~/data/screenshots/` |

> 🔧 **For complete configuration details and advanced options, see [Design.md](./Design.md#configuration-system)**

## 🏗️ Project Structure

```
screenAgent/
├── main.py                    # Application entry point
├── screenshots/               # 📁 Persistent screenshot storage (file-based)
│   └── run_YYYYMMDD_HHMMSS_<uuid>/  # Unique directories per app run
│       ├── <uuid>.png         # Screenshot files with metadata
│       └── metadata.json      # Screenshot index and metadata
├── temp/                      # 📁 Temporary files (ROI selection, previews)
│   └── temp_screenshot.png    # Temporary screenshot for ROI selection
├── src/                       # Source code modules
│   ├── core/                  # Core functionality (modular architecture)
│   │   ├── capture/           # Screenshot capture implementations
│   │   │   ├── __init__.py
│   │   │   ├── capture_interfaces.py      # Abstract capture interfaces
│   │   │   ├── capture_implementations.py # Platform-specific capture
│   │   │   └── screenshot_capture.py       # Unified capture manager
│   │   ├── config/            # Configuration management
│   │   │   ├── __init__.py
│   │   │   └── config.py      # Centralized configuration
│   │   ├── events/            # Event system for component communication
│   │   │   ├── __init__.py
│   │   │   └── events.py      # Event types and dispatcher
│   │   ├── monitoring/        # ROI monitoring and change detection
│   │   │   ├── __init__.py
│   │   │   ├── change_detection.py        # Pluggable detection strategies
│   │   │   └── roi_monitor_refactored.py  # Event-driven monitor
│   │   └── storage/           # Data storage and management
│   │       ├── __init__.py
│   │       ├── storage_manager.py         # Storage abstraction layer
│   │       ├── screenshot_orchestrator.py # Orchestrates all operations
│   │       └── screenshot_manager_refactored.py # Clean API wrapper
│   ├── api/                   # Web server and AI integration
│   │   ├── server.py          # HTTP server and REST API
│   │   └── llm_api.py         # Multi-provider AI analysis
│   ├── models/                # Data models and schemas
│   ├── services/              # Service layer abstractions
│   ├── utils/                 # Utility modules
│   │   ├── keyboard_handler.py    # Global hotkey support
│   │   └── platform_detection.py  # OS/environment detection
│   └── ui/                    # User interface components
├── static/                    # Web assets
│   ├── css/style.css         # Modern responsive CSS
│   └── js/app.js             # Interactive frontend
├── templates/                 # HTML templates
│   ├── index.html            # Main dashboard
│   └── select_roi.html       # ROI selection interface
├── tests/                     # Test suite
│   ├── test_phase_1_4_basic.py           # Phase 1.4 validation
│   ├── test_screenshot_manager_refactor.py # Comprehensive tests
│   └── test_screenshot_manager_simple.py  # Simplified test suite
├── docs/                      # Documentation
│   ├── Design.md             # Comprehensive system design
│   ├── PHASE_1_4_SUMMARY.md  # Latest refactoring summary
│   └── REFACTORING_TODO.md   # Development roadmap
├── legacy/                    # Original implementation (preserved)
├── config/                    # Configuration files
└── requirements.txt          # Python dependencies
```

> 🏗️ **For detailed architecture and design patterns, see [Design.md](./Design.md#architecture)**

## 🔧 Modular Architecture (Phase 1.4)

ScreenAgent has been refactored into a modern, modular architecture for improved maintainability and extensibility:

### **Storage Abstraction Layer**
- **Multiple Storage Backends**: Memory and file system storage with pluggable architecture
- **File-Based Storage Default**: Screenshots persist to disk in organized run directories
- **Unique Run Directories**: Each app session gets isolated storage to prevent conflicts
- **Metadata Management**: Comprehensive screenshot metadata with timestamps, ROI info, and analysis results
- **Automatic Cleanup**: Configurable size limits with automatic old screenshot removal
- **Thread-Safe Operations**: Proper locking mechanisms for concurrent access

### **Screenshot Orchestrator**
- **Event-Driven Coordination**: Centralized orchestration of all screenshot operations
- **Component Communication**: Event system connecting capture, monitoring, and storage
- **Performance Monitoring**: Built-in statistics and health monitoring
- **Graceful Error Handling**: Comprehensive error recovery strategies

### **Modular Capture System**
- **Platform Abstraction**: Clean interfaces with multiple capture implementations
- **Automatic Fallbacks**: Multiple capture methods with intelligent fallback strategies
- **Factory Pattern**: Dynamic selection of optimal capture method per platform

### **Enhanced Monitoring**
- **Pluggable Detection**: Multiple change detection algorithms
- **Event System**: Real-time communication between components
- **Performance Metrics**: Detailed monitoring statistics and health checks

**Architecture Benefits:**
- ✅ **Separation of Concerns**: Each module has a single, clear responsibility
- ✅ **Testability**: Components can be tested independently
- ✅ **Extensibility**: Easy to add new storage backends or capture methods  
- ✅ **Maintainability**: Clear interfaces and minimal coupling
- ✅ **Backward Compatibility**: Existing code continues to work with wrapper layer

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

### Development Status
**✅ Phase 1.4 Complete (June 2025)**: Major refactoring to modular architecture
- Modular storage system with multiple backends
- Event-driven screenshot orchestration
- Enhanced component testability and maintainability
- Comprehensive error handling and recovery

**🚀 Upcoming**: Phase 1.5 - Keyboard Handler refactoring, Service Layer creation

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
- `tests/test_phase_1_4_basic.py` - Phase 1.4 refactoring validation
- `tests/test_screenshot_manager_refactor.py` - Comprehensive refactored component tests
- `tests/test_screenshot_manager_simple.py` - Simplified test suite
- `test_basic.py` - Core functionality tests (legacy)
- `test_comprehensive_screenshot.py` - Screenshot capture tests (legacy)
- `test_roi_functionality.py` - ROI monitoring tests (legacy)
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

**📋 For comprehensive documentation:**
- **[Design.md](./docs/Design.md)** - Complete system architecture and technical details
- **[PHASE_1_4_SUMMARY.md](./docs/PHASE_1_4_SUMMARY.md)** - Latest refactoring summary and achievements
- **[REFACTORING_TODO.md](./docs/REFACTORING_TODO.md)** - Development roadmap and future plans

## 🔧 Frontend Refactoring (React Migration)

**🚀 New React Frontend Available**: ScreenAgent now includes a modern React-based frontend alongside the original vanilla JavaScript interface.

### React Frontend Features
- **Modern Architecture**: React 18 + TypeScript + Tailwind CSS
- **Modular Design**: Component-based architecture for better maintainability  
- **Enhanced Performance**: Optimized bundling and lazy loading
- **Future-Ready**: Prepared for projects, chat AI, voice features, and multi-model comparison

### Quick Start with React Frontend

```bash
# Setup React frontend (one-time)
./scripts/setup_react_frontend.sh

# Start development
cd frontend
npm run dev  # React frontend (port 3000)

# In another terminal
cd /home/alibina/repo/screenAgent
python main.py  # Python backend (port 8000)
```

**Accessing the Application:**
- **React Frontend**: http://localhost:3000 (recommended for development)
- **Legacy Frontend**: http://localhost:8000 (original vanilla JS interface)

### Migration Status
- ✅ **Phase 1 Complete**: React foundation, component structure, development environment
- 🚧 **Phase 2 In Progress**: State management, API integration, UI components
- 📋 **Upcoming**: Core feature migration, advanced features, testing

**Documentation:**
- **[React Setup Guide](./docs/react_setup_guide.md)** - Getting started with React frontend
- **[Frontend Refactoring Plan](./docs/frontend_refactoring_todo.md)** - Detailed migration roadmap

### For Production Use
The legacy vanilla JavaScript frontend remains fully functional. The React frontend is currently in development and recommended for contributors and advanced users.

> 📋 **The React migration is designed to be non-disruptive** - both frontends can run simultaneously during the transition period.