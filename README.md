# ScreenAgent 🎯

A modern, intelligent screen monitoring application that captures and analyzes changes within user-defined regions of interest (ROI) using AI-powered analysis. Built with a modular, event-driven architecture for enhanced maintainability and extensibility.

## ✨ Key Features

- **🎯 Smart ROI Monitoring**: Interactive region selection with real-time change detection
- **🤖 AI-Powered Analysis**: Multi-provider AI integration (OpenAI GPT-4 Vision, Azure AI)
- **✏️ Dynamic Prompt Management**: Editable AI analysis prompts with real-time updates
- **🌐 Modern Web Interface**: Responsive dashboard with real-time updates and screenshot gallery
- **📱 Cross-Platform**: Seamless operation on Linux, Windows, and WSL environments
- **⚙️ Flexible Configuration**: Web-based settings with dynamic updates
- **⌨️ Keyboard Shortcuts**: Global hotkeys for manual screenshot capture
- **📊 Real-time Statistics**: Monitor uptime, capture count, and system performance
- **🏗️ Modular Architecture**: Event-driven design with pluggable storage and capture backends


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

2. **Install Flask dependencies:**
   ```bash
   pip install flask flask-restx flask-cors flask-injector pytest pytest-flask pytest-asyncio
   ```

3. **Configure AI (optional):**
   ```bash
   # Create .env file or set environment variables
   export OPENAI_API_KEY="your-openai-api-key"
   # OR
   export AZURE_AI_ENDPOINT="your-azure-endpoint"
   export AZURE_AI_API_KEY="your-azure-api-key"
   ```

4. **Start ScreenAgent:**
   ```bash
   # Modern Flask-based API (recommended)
   python main_flask.py
   
   # OR legacy interface (for compatibility)
   python main.py
   ```

5. **Access the application:**
   - **API Documentation:** `http://localhost:8000/docs/` (Swagger UI)
   - **React Frontend:** `http://localhost:3000` (when frontend is running)
   - **Health Check:** `http://localhost:8000/api/config/health`

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
- **Editable Prompts**: Inline editing of analysis prompts with auto-save
- **Management**: View, download, or delete individual/all screenshots

### ⚙️ Settings
- **Monitoring**: Sensitivity, interval, and threshold configuration
- **AI Options**: Provider selection, model choice, editable custom prompts
- **Preferences**: Auto-start, keyboard shortcuts, display options

## 🌐 REST API Endpoints

ScreenAgent provides a comprehensive REST API with Swagger documentation at `/docs/`:

### 📸 Screenshot Management
- `GET /api/screenshots/list` - Get all screenshots with metadata
- `POST /api/screenshots/capture` - Take a new screenshot
- `GET /api/screenshots/{id}` - Get specific screenshot by ID
- `DELETE /api/screenshots/clear` - Delete all screenshots
- `GET /api/screenshots/preview` - Get live preview image

### 📊 Monitoring Control  
- `GET /api/monitoring/status` - Get monitoring status and statistics
- `POST /api/monitoring/start` - Start ROI monitoring with settings
- `POST /api/monitoring/stop` - Stop monitoring and get session summary
- `POST /api/monitoring/roi` - Update region of interest coordinates

### ⚙️ Configuration Management
- `GET /api/config/health` - Service health check
- `GET /api/config/status` - Get application status and uptime
- `GET /api/config/get` - Get current configuration
- `POST /api/config/set` - Update configuration settings

### 🤖 AI Analysis
- `POST /api/analysis/analyze` - Analyze screenshot with AI
- `POST /api/analysis/compare` - Compare two screenshots for changes
- `GET /api/analysis/models` - Get available AI models

### ✏️ Prompt Management
- `GET /api/prompts/` - Get all available analysis prompts
- `GET /api/prompts/{prompt_id}` - Get specific prompt by ID
- `PUT /api/prompts/{prompt_id}` - Update specific prompt text and metadata

> 📚 **Complete API documentation with examples and schemas available at `/docs/` when running the application**

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
├── main.py                    # Legacy entry point (supports old interface)
├── main_flask.py              # 🆕 Flask-based entry point (modern API)
├── screenshots/               # 📁 Persistent screenshot storage (file-based)
│   └── run_YYYYMMDD_HHMMSS_<uuid>/  # Unique directories per app run
│       ├── <uuid>.png         # Screenshot files with metadata
│       └── metadata.json      # Screenshot index and metadata
├── temp/                      # 📁 Temporary files (ROI selection, previews)
│   └── temp_screenshot.png    # Temporary screenshot for ROI selection
├── src/                       # Source code modules
│   ├── api/                   # 🆕 Flask-based REST API with Swagger
│   │   ├── flask_app.py       # Flask application factory
│   │   ├── blueprints/        # Modular API endpoints
│   │   │   ├── screenshots.py # Screenshot management endpoints
│   │   │   ├── monitoring.py  # ROI monitoring endpoints
│   │   │   ├── configuration.py # Settings and config endpoints
│   │   │   ├── analysis.py    # AI analysis endpoints
│   │   │   └── prompts.py     # 🆕 AI prompt management endpoints
│   │   ├── middleware/        # Request/response middleware
│   │   │   ├── error_handler.py # Centralized error handling
│   │   │   ├── logging_middleware.py # Request logging
│   │   │   ├── validation.py  # Request validation
│   │   │   └── security.py    # Security headers and CORS
│   │   └── models/            # Swagger/OpenAPI models
│   │       └── swagger_models.py # API documentation models
│   ├── domain/                # 🆕 Clean architecture domain layer
│   │   ├── entities/          # Core business entities
│   │   ├── exceptions/        # Domain-specific exceptions
│   │   ├── interfaces/        # Abstract service interfaces
│   │   └── repositories/      # Data access interfaces
│   ├── application/           # 🆕 Application services layer
│   │   └── services/          # Business logic implementations
│   ├── infrastructure/        # 🆕 Infrastructure implementations
│   │   ├── dependency_injection/ # DI container and setup
│   │   ├── repositories/      # Concrete repository implementations
│   │   └── storage/           # Storage backends and factories
│   ├── interfaces/            # 🆕 Interface adapters (controllers)
│   │   └── controllers/       # API controllers for business logic
│   └── utils/                 # Utility modules
│       ├── keyboard_handler.py    # Global hotkey support
│       └── platform_detection.py  # OS/environment detection
├── frontend/                  # 🆕 Modern React frontend
│   ├── src/                   # React source code
│   │   ├── components/        # Reusable UI components
│   │   │   └── ui/            # UI components including PromptEditor
│   │   ├── services/          # API client services (including promptsApi)
│   │   └── stores/            # State management
│   ├── package.json           # Node.js dependencies
│   └── vite.config.ts         # Build configuration
├── tests/                     # Test suite
│   ├── api/                   # 🆕 Flask API tests
│   │   ├── test_screenshots.py    # Screenshot endpoint tests
│   │   ├── test_monitoring.py     # Monitoring endpoint tests
│   │   ├── test_configuration.py  # Configuration endpoint tests
│   │   ├── test_analysis.py       # Analysis endpoint tests
│   │   └── test_integration.py    # End-to-end API tests
│   ├── test_clean_architecture.py # Clean architecture validation
│   └── test_simple.py             # Basic import tests
├── docs/                      # Documentation
│   ├── Design.md             # Comprehensive system design
│   ├── DESIGN_ANALYSIS.md    # Backend analysis and API flows
│   ├── REFACTORING_PLAN.md   # Flask migration plan and progress
│   └── CLEAN_ARCHITECTURE_MIGRATION_SUCCESS.md # Migration summary
├── config/                    # Configuration files
│   ├── screen_agent_config.json # Application configuration
│   └── prompts/               # 🆕 AI analysis prompts
│       └── image_analysis.json # Editable analysis prompts with metadata
└── requirements.txt          # Python dependencies
```

> 🏗️ **For detailed architecture and design patterns, see [Design.md](./Design.md#architecture)**

## 🔧 Modern Flask-based Architecture (Phase 2.0)

ScreenAgent has been completely refactored from a custom HTTP server to a modern Flask-based REST API with clean architecture:

### **🌐 Flask REST API with Swagger Documentation**
- **Flask-RESTX Integration**: Auto-generated OpenAPI/Swagger documentation at `/docs/`
- **Modular Blueprints**: Organized endpoints by feature area (screenshots, monitoring, config, analysis)
- **Comprehensive Middleware**: Error handling, request validation, security headers, and CORS
- **Clean Architecture**: Dependency injection with domain-driven design principles

### **🏗️ Clean Architecture Layers**
- **Domain Layer**: Core business entities, interfaces, and domain-specific exceptions
- **Application Layer**: Business logic services implementing domain interfaces  
- **Infrastructure Layer**: Concrete implementations for storage, repositories, and external services
- **Interface Layer**: Controllers handling HTTP requests and responses
- **Dependency Injection**: Centralized container managing all service dependencies

### **📊 Enhanced API Features**
- **Structured Error Responses**: Consistent JSON error format with detailed messages
- **Request Validation**: Automatic validation with descriptive error messages
- **Security Headers**: CORS, CSP, and security headers for production deployment
- **Performance Monitoring**: Request timing and error tracking middleware

### **🧪 Comprehensive Testing**
- **API Test Suite**: 88 comprehensive tests covering all endpoints
- **Test Coverage**: Authentication, validation, error handling, and business logic
- **Integration Tests**: End-to-end testing of complete user workflows
- **Clean Architecture Tests**: Validation of dependency injection and service resolution

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
- **Editable Custom Prompts**: Real-time prompt editing with auto-save functionality

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
**✅ Phase 2.0 Complete (June 2025)**: Flask-based REST API with clean architecture
- Complete migration from custom HTTP server to Flask + Flask-RESTX
- Clean architecture with dependency injection and domain-driven design
- Comprehensive Swagger/OpenAPI documentation
- 88 comprehensive API tests with 85% pass rate
- Modular blueprint structure with middleware pipeline
- Enhanced error handling and request validation

**✅ Phase 1.4 Complete (June 2025)**: Major refactoring to modular architecture
- Modular storage system with multiple backends
- Event-driven screenshot orchestration
- Enhanced component testability and maintainability
- Comprehensive error handling and recovery

**🚀 Upcoming**: Frontend React migration, performance optimizations, deployment automation

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/screenAgent.git
cd screenAgent

# Install dependencies
pip install -r requirements.txt
pip install flask flask-restx flask-cors flask-injector pytest pytest-flask pytest-asyncio

# Run tests
pytest tests/api/ -v

# Start development server
python main_flask.py
```

### Testing
- `tests/api/` - **🆕 Flask API test suite** (88 comprehensive tests)
  - `test_screenshots.py` - Screenshot endpoint tests
  - `test_monitoring.py` - Monitoring endpoint tests  
  - `test_configuration.py` - Configuration endpoint tests
  - `test_analysis.py` - Analysis endpoint tests
  - `test_integration.py` - End-to-end workflow tests
- `tests/test_clean_architecture.py` - Clean architecture validation
- `tests/test_simple.py` - Basic import and component tests

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs/` - Interactive API documentation
- **OpenAPI Spec**: `http://localhost:8000/docs/swagger.json` - Machine-readable API spec
- **Health Check**: `http://localhost:8000/api/config/health` - Service health status

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