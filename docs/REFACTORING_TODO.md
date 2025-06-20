# ScreenAgent Refactoring Plan - Modularization & Logging

## Overview
This refactoring aims to improve code modularity, maintainability, and add proper logging infrastructure without adding new features. The plan follows a systematic approach to modularize the codebase and implement comprehensive logging.

## Phase 1: Core Module Restructuring

### 1.1 Configuration Management Module ✅ (Already well-structured)
- **Status**: ✅ Config class is already well-modularized
- **File**: `src/core/config.py`
- **Notes**: Good separation of concerns, proper type hints, clear interface

### 1.2 Screenshot Capture Module Refactoring ✅ COMPLETED
- **File**: `src/core/screenshot_capture.py`
- **Current Issues**: RESOLVED
- **Actions Completed**:
  - [x] Extract platform-specific capture methods into separate classes
  - [x] Create abstract base capture interface (`capture_interfaces.py`)
  - [x] Implement factory pattern for capture method selection
  - [x] Add comprehensive error handling with recovery strategies
  - [x] Create capture result data classes for better type safety
- **New Files Created**:
  - `src/core/capture_interfaces.py` - Abstract interfaces and factory
  - `src/core/capture_implementations.py` - Platform-specific implementations
  - `src/core/screenshot_capture_refactored.py` - New manager with fallback strategies
- **Performance Results**: ✅ All tests passed, 3 capture methods available with automatic fallback

### 1.3 ROI Monitor Module Refactoring ✅ COMPLETED
- **File**: `src/core/roi_monitor.py`
- **Current Issues**: RESOLVED
- **Actions Completed**:
  - [x] Separate change detection algorithms into pluggable strategies
  - [x] Create ROI change event system with proper callbacks
  - [x] Abstract monitoring loop from change detection
  - [x] Add performance metrics collection
  - [x] Implement configurable sensitivity algorithms
- **New Files Created**:
  - `src/core/change_detection.py` - Modular change detection strategies
  - `src/core/events.py` - Event system for component communication
  - `src/core/roi_monitor_refactored.py` - New monitor with event-driven architecture
- **Performance Results**: ✅ 17/17 tests passed, 4 detection methods available, event system working

### 1.4 Screenshot Manager Module Refactoring ✅ COMPLETED
- **File**: `src/core/screenshot_manager.py`
- **Current Issues**: RESOLVED
- **Actions Completed**:
  - [x] Extract storage logic into separate StorageManager
  - [x] Create ScreenshotOrchestrator for coordination
  - [x] Implement event-driven architecture for component communication
  - [x] Add proper lifecycle management
  - [x] Create screenshot metadata management system
- **New Files Created**:
  - `src/core/storage_manager.py` - Storage abstraction with multiple backends
  - `src/core/screenshot_orchestrator.py` - Orchestrates all screenshot operations
  - `src/core/screenshot_manager_refactored.py` - New manager with modular architecture
- **Performance Results**: ✅ All tests passed, storage and orchestration working correctly

### 1.X File Structure Restructuring ✅ COMPLETED
- **Scope**: Entire codebase organization
- **Current Issues**: RESOLVED
- **Actions Completed**:
  - [x] Reorganize modules by functional areas (capture, monitoring, storage, events, config)
  - [x] Create logical directory hierarchy reflecting modular architecture  
  - [x] Centralize tests, configuration files, documentation, and scripts
  - [x] Update import statements to use relative imports within modules
  - [x] Create comprehensive __init__.py files with proper exports
  - [x] Preserve legacy files for backward compatibility reference
- **New Structure Created**:
  - `src/core/capture/` - Screenshot capture functionality
  - `src/core/monitoring/` - ROI monitoring functionality
  - `src/core/storage/` - Data storage and management
  - `src/core/events/` - Event system
  - `src/core/config/` - Configuration management
  - `src/utils/` - Platform utilities and helpers
  - `tests/` - All test files centralized
  - `config/` - Configuration files
  - `docs/` - Documentation and planning
  - `scripts/` - Utility scripts
  - `legacy/` - Original files preserved for reference
- **Benefits Achieved**: Clear separation of concerns, improved discoverability, enhanced testability, better maintenance

### 1.5 Keyboard Handler Module Refactoring
- **File**: `src/core/keyboard_handler.py`  
- **Current Issues**:
  - Platform-specific code not well separated
  - Limited key binding configuration
  - No abstraction for different input methods
- **Actions**:
  - [ ] Create platform-specific keyboard implementations
  - [ ] Add configurable key binding system
  - [ ] Implement input event abstraction layer
  - [ ] Add graceful degradation for unsupported platforms

## Phase 2: Service Layer Creation

### 2.1 Create Service Abstractions
- **New Directory**: `src/services/`
- **Actions**:
  - [ ] Create `screenshot_service.py` for high-level screenshot operations
  - [ ] Create `monitoring_service.py` for ROI monitoring coordination
  - [ ] Create `storage_service.py` for data persistence
  - [ ] Create `event_service.py` for inter-component communication

### 2.2 Implement Event System
- **New File**: `src/core/events.py`
- **Actions**:
  - [ ] Create event base classes and types
  - [ ] Implement event dispatcher/subscriber pattern
  - [ ] Add event middleware for logging and debugging
  - [ ] Create typed events for better IDE support

## Phase 3: API Layer Refactoring

### 3.1 HTTP Server Module Refactoring
- **File**: `src/api/server.py`
- **Current Issues**:
  - Monolithic handler class with too many responsibilities
  - API routing mixed with request handling
  - No clear separation between business logic and HTTP concerns
- **Actions**:
  - [ ] Extract API routes into separate route modules
  - [ ] Create middleware system for request/response handling
  - [ ] Implement proper HTTP status and error handling
  - [ ] Add request validation and response serialization
  - [ ] Separate static file serving from API handling

### 3.2 LLM Integration Refactoring
- **File**: `src/api/llm_api.py`
- **Current Issues**:
  - Direct API client management in business logic
  - Limited provider abstraction
  - No proper retry and fallback mechanisms
- **Actions**:
  - [ ] Create provider abstraction layer
  - [ ] Implement retry and circuit breaker patterns
  - [ ] Add response caching system
  - [ ] Create prompt template system
  - [ ] Add usage analytics and rate limiting

## Phase 4: Data and Storage Layer

### 4.1 Create Data Models
- **New Directory**: `src/models/`
- **Actions**:
  - [ ] Create `screenshot.py` for screenshot data models
  - [ ] Create `roi.py` for ROI configuration models
  - [ ] Create `settings.py` for configuration models
  - [ ] Add data validation and serialization

### 4.2 Storage Abstraction
- **New Directory**: `src/storage/`
- **Actions**:
  - [ ] Create abstract storage interface
  - [ ] Implement file system storage backend
  - [ ] Add metadata indexing system
  - [ ] Create storage migration system for future extensions

## Phase 5: Utilities and Common Infrastructure

### 5.1 Error Handling Infrastructure
- **New File**: `src/core/exceptions.py`
- **Actions**:
  - [ ] Create custom exception hierarchy
  - [ ] Add error context and recovery suggestions
  - [ ] Implement error reporting and analytics
  - [ ] Create error boundary patterns

### 5.2 Performance and Metrics
- **New File**: `src/core/metrics.py`
- **Actions**:
  - [ ] Create performance monitoring system
  - [ ] Add memory usage tracking
  - [ ] Implement operation timing and profiling
  - [ ] Create health check endpoints

## Phase 6: Comprehensive Logging System

### 6.1 Logging Infrastructure
- **New File**: `src/core/logging.py`
- **Actions**:
  - [ ] Create centralized logging configuration
  - [ ] Implement structured logging with JSON format
  - [ ] Add log rotation and archiving
  - [ ] Create log filtering and sampling
  - [ ] Add contextual logging (request IDs, session tracking)

### 6.2 Component-Specific Loggers
- **Actions**:
  - [ ] Add logger to each major component
  - [ ] Implement debug mode with verbose logging
  - [ ] Add performance logging for critical operations
  - [ ] Create audit logging for user actions
  - [ ] Add error tracking and notification system

### 6.3 Logging Integration
- **Actions**:
  - [ ] Integrate logging with error handling
  - [ ] Add logging middleware to HTTP server
  - [ ] Create logging dashboard in web interface
  - [ ] Add log export functionality
  - [ ] Implement log-based monitoring and alerting

## Testing and Validation Plan

### Performance Testing
After each module refactoring:
- [ ] Measure memory usage before/after
- [ ] Test screenshot capture performance
- [ ] Validate ROI monitoring accuracy
- [ ] Check web interface responsiveness
- [ ] Verify multi-threading stability

### Integration Testing
- [ ] Test component communication after refactoring
- [ ] Validate configuration system integration
- [ ] Check error handling and recovery
- [ ] Test cross-platform compatibility
- [ ] Validate logging output and performance impact

## Implementation Order

1. **Phase 1.1-1.2**: Screenshot Capture Module (Week 1)
2. **Phase 1.3**: ROI Monitor Module (Week 1)
3. **Phase 1.4**: Screenshot Manager Module (Week 2)
4. **Phase 2.1-2.2**: Service Layer Creation (Week 2)
5. **Phase 3.1**: HTTP Server Refactoring (Week 3)
6. **Phase 4.1-4.2**: Data and Storage Layer (Week 3)
7. **Phase 5.1-5.2**: Utilities and Infrastructure (Week 4)
8. **Phase 6.1-6.3**: Comprehensive Logging (Week 4)

## Success Criteria

### Modularity Goals
- [ ] Each module has single responsibility
- [ ] Clear interfaces between components
- [ ] Minimal coupling between modules
- [ ] Easy to test individual components
- [ ] Configurable component behavior

### Logging Goals
- [ ] Comprehensive logging coverage
- [ ] Structured, searchable log format
- [ ] Performance impact < 5% overhead
- [ ] Easy debugging and troubleshooting
- [ ] Proper log level management

### Performance Goals
- [ ] No degradation in screenshot capture speed
- [ ] Memory usage remains stable
- [ ] Web interface responsiveness maintained
- [ ] Startup time not significantly increased
- [ ] Graceful handling of high-frequency operations

## Notes
- Each phase will be implemented and tested before moving to the next
- Performance benchmarks will be recorded before and after each change
- Rollback plans will be prepared for each major refactoring
- Documentation will be updated as modules are refactored
- Backward compatibility will be maintained for configuration files

---
**Status**: 🚀 Ready to begin Phase 1.2 - Screenshot Capture Module Refactoring
**Last Updated**: June 20, 2025
**Next Review**: After Phase 1.2 completion