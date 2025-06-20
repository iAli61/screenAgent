# ScreenAgent - Restructured File Organization

## New Modular Architecture

The ScreenAgent codebase has been restructured to better represent the modular architecture developed during the refactoring process. This new organization improves maintainability, testability, and extensibility.

## Directory Structure

```
screenAgent/
├── src/                              # Source code
│   ├── core/                        # Core business logic modules
│   │   ├── capture/                 # Screenshot capture functionality
│   │   │   ├── __init__.py
│   │   │   ├── capture_interfaces.py      # Abstract interfaces
│   │   │   ├── capture_implementations.py # Platform-specific implementations
│   │   │   ├── screenshot_capture.py      # Legacy capture module
│   │   │   └── screenshot_capture_refactored.py  # New modular manager
│   │   ├── monitoring/              # ROI monitoring functionality
│   │   │   ├── __init__.py
│   │   │   ├── change_detection.py        # Pluggable change detection strategies
│   │   │   ├── roi_monitor.py             # Legacy monitor
│   │   │   └── roi_monitor_refactored.py  # New event-driven monitor
│   │   ├── storage/                 # Data storage and management
│   │   │   ├── __init__.py
│   │   │   ├── storage_manager.py         # Storage abstraction layer
│   │   │   ├── screenshot_orchestrator.py # Operations orchestrator
│   │   │   ├── screenshot_manager.py      # Legacy manager
│   │   │   └── screenshot_manager_refactored.py  # New modular manager
│   │   ├── events/                  # Event system
│   │   │   ├── __init__.py
│   │   │   └── events.py                  # Event-driven communication
│   │   ├── config/                  # Configuration management
│   │   │   ├── __init__.py
│   │   │   └── config.py                  # Centralized configuration
│   │   └── __init__.py              # Core module exports
│   ├── services/                    # High-level service layer (future)
│   │   └── __init__.py
│   ├── api/                        # HTTP API and LLM integration
│   │   ├── __init__.py
│   │   ├── server.py               # HTTP server
│   │   └── llm_api.py              # LLM integration
│   ├── models/                     # Data models and schemas (future)
│   │   └── __init__.py
│   ├── utils/                      # Utility modules
│   │   ├── __init__.py
│   │   ├── platform_detection.py  # Platform detection utilities
│   │   └── keyboard_handler.py     # Keyboard input handling
│   └── ui/                         # Web interface
│       └── (existing files)
├── tests/                          # All test files
│   ├── __init__.py
│   ├── test_phase_1_4_basic.py
│   ├── test_screenshot_manager_refactor.py
│   ├── test_screenshot_manager_simple.py
│   ├── test_screenshot_refactor.py
│   ├── test_roi_monitor_refactor.py
│   ├── verify_refactor.py
│   └── (other test files)
├── config/                         # Configuration files
│   ├── screen_agent_config.json
│   └── .env.example
├── docs/                          # Documentation
│   ├── Design.md
│   ├── planned_features.md
│   ├── PHASE_1_4_SUMMARY.md
│   └── REFACTORING_TODO.md
├── scripts/                       # Utility scripts
│   ├── install.py
│   ├── azure_config_check.py
│   ├── screenshot_script.ps1
│   └── docx_to_markdown.py
├── legacy/                        # Legacy files (for reference)
│   ├── config.py
│   ├── keyboard_handler.py
│   ├── llm_handler.py
│   ├── platform_detection.py
│   ├── screenshot.py
│   ├── screenshot_server.py
│   └── server_handler.py
├── static/                        # Static web assets
├── templates/                     # Web templates
├── screenshots/                   # Screenshot storage
├── main.py                        # Application entry point
└── (configuration and requirement files)
```

## Module Responsibilities

### Core Modules (`src/core/`)

#### Capture Module (`src/core/capture/`)
- **Purpose**: Screenshot capture with multiple backends
- **Key Components**:
  - Abstract interfaces for capture methods
  - Platform-specific implementations (PIL, PyAutoGUI, Scrot, PowerShell)
  - Capture manager with automatic fallback strategies
  - Type-safe capture results

#### Monitoring Module (`src/core/monitoring/`)
- **Purpose**: ROI monitoring with pluggable change detection
- **Key Components**:
  - Abstract change detection strategies
  - Multiple detection algorithms (size, hash, pixel difference, advanced)
  - Event-driven monitor with configurable sensitivity
  - Performance metrics collection

#### Storage Module (`src/core/storage/`)
- **Purpose**: Screenshot storage and management
- **Key Components**:
  - Storage abstraction with multiple backends (memory, filesystem)
  - Screenshot orchestrator for operation coordination
  - Metadata management and analysis response storage
  - Thread-safe operations with automatic cleanup

#### Events Module (`src/core/events/`)
- **Purpose**: Event-driven communication between components
- **Key Components**:
  - Typed event system with subscription management
  - Screenshot captured and change detected events
  - Event dispatcher for decoupled communication

#### Config Module (`src/core/config/`)
- **Purpose**: Centralized configuration management
- **Key Components**:
  - Type-safe configuration with validation
  - Environment variable support
  - Default value management

### Service Layer (`src/services/`)
- **Status**: Planned for Phase 2
- **Purpose**: High-level business logic coordination
- **Planned Components**: Screenshot service, monitoring service, storage service

### API Layer (`src/api/`)
- **Purpose**: HTTP API and external integrations
- **Components**: Web server, LLM API integration

### Models (`src/models/`)
- **Status**: Planned for Phase 4  
- **Purpose**: Data models and validation schemas

### Utils (`src/utils/`)
- **Purpose**: Platform utilities and helpers
- **Components**: Platform detection, keyboard handling

## Import Structure

The new structure uses relative imports to maintain clear dependencies:

```python
# Core modules import from each other
from ..config import Config
from ..events import emit_event
from ..capture import ScreenshotCaptureManager

# Services layer imports from core
from ..core.storage import ScreenshotOrchestrator

# API layer imports from core and services  
from ..core.config import Config
from ..services.screenshot_service import ScreenshotService

# Utils can import from core
from ..core.config import Config
```

## Benefits of New Structure

### 1. **Clear Separation of Concerns**
- Each module has a single, well-defined responsibility
- Dependencies flow in one direction (no circular imports)
- Easy to understand what each module does

### 2. **Improved Testability**
- Each module can be tested independently
- Test files are organized in a dedicated directory
- Clear interfaces make mocking easier

### 3. **Enhanced Maintainability**
- Related code is grouped together
- Easy to find and modify specific functionality
- Reduced cognitive load when working on features

### 4. **Better Extensibility**
- New capture methods can be added to capture/
- New storage backends can be added to storage/
- New change detection algorithms can be added to monitoring/

### 5. **Documentation and Discovery**
- Module structure is self-documenting
- __init__.py files clearly export public APIs
- Easy to navigate codebase for new developers

## Migration Notes

### Import Updates
All import statements have been updated to reflect the new structure. The changes maintain backward compatibility where possible.

### Legacy Files
Original files are preserved in the `legacy/` directory for reference during the transition period.

### Test Organization  
All test files are now in the `tests/` directory with clear naming conventions.

### Configuration Files
Configuration files are centralized in the `config/` directory.

## Future Phases

The new structure sets the foundation for the remaining refactoring phases:

- **Phase 2**: Service layer implementation in `src/services/`
- **Phase 3**: API refactoring in `src/api/`
- **Phase 4**: Data models in `src/models/`
- **Phase 5**: Enhanced utilities in `src/utils/`
- **Phase 6**: Comprehensive logging throughout all modules

This restructured organization provides a solid foundation for continued development and maintenance of the ScreenAgent application.
