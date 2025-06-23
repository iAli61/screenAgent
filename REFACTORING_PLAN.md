# ScreenAgent Backend - Detailed Refactoring Plan

**Date**: June 22, 2025  
**Phase**: Phase 2 - Detailed Refactoring Plan  
**Based On**: DESIGN_ANALYSIS.md findings  
**Execution Status**: Ready for Implementation

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Architectural Changes](#architectural-changes)
3. [Code Refactoring](#code-refactoring)
4. [Redundancy Removal](#redundancy-removal)
5. [Implementation Order](#implementation-order)
6. [Testing Strategy](#testing-strategy)
7. [Risk Assessment](#risk-assessment)

## Executive Summary

This refactoring plan addresses the critical architectural issues identified in the design analysis. The primary goals are:

1. **Introduce Service Layer**: Separate business logic from infrastructure
2. **Implement Dependency Injection**: Enable better testing and loose coupling
3. **Create Domain Models**: Establish clear data structures
4. **Reorganize Module Structure**: Follow clean architecture principles
5. **Eliminate Redundancy**: Remove duplicate and unused code

**Estimated Impact**: 
- **Lines Changed**: ~2,000-3,000 lines
- **Files Modified**: ~15-20 files
- **New Files Created**: ~10-15 files
- **Files Removed**: ~3-5 files

## Architectural Changes

### 1. Service Layer Implementation
**Priority**: 🔴 **Critical**  
**Timeline**: Phase 2.1 (Days 1-3)

#### 1.1 Create Service Interfaces
- [ ] **Create `src/application/interfaces/`** directory
  - **File**: `src/application/interfaces/__init__.py`
  - **File**: `src/application/interfaces/screenshot_service.py`
  - **File**: `src/application/interfaces/monitoring_service.py`
  - **File**: `src/application/interfaces/analysis_service.py`
  - **File**: `src/application/interfaces/configuration_service.py`
  - **Reason**: Establish clear contracts for business operations
  - **Impact**: Enables dependency injection and testing

#### 1.2 Implement Service Classes
- [ ] **Create `src/application/services/`** directory
  - **File**: `src/application/services/screenshot_service_impl.py`
  - **File**: `src/application/services/monitoring_service_impl.py`
  - **File**: `src/application/services/analysis_service_impl.py`
  - **File**: `src/application/services/configuration_service_impl.py`
  - **Reason**: Centralize business logic and reduce coupling
  - **Impact**: Simplifies testing and maintenance

### 2. Domain Model Creation
**Priority**: 🔴 **Critical**  
**Timeline**: Phase 2.1 (Days 1-2)

#### 2.1 Create Core Domain Models
- [x] **Create `src/domain/entities/`** directory
  - **File**: `src/domain/entities/screenshot.py` ✅ **COMPLETED**
  - **File**: `src/domain/entities/roi_region.py` ✅ **COMPLETED**
  - **File**: `src/domain/entities/monitoring_session.py` ✅ **COMPLETED**
  - **File**: `src/domain/entities/analysis_result.py` ✅ **COMPLETED**
  - **Reason**: Establish clear data structures with behavior
  - **Impact**: Reduces primitive obsession and improves type safety

#### 2.2 Create Value Objects
- [x] **Create `src/domain/value_objects/`** directory
  - **File**: `src/domain/value_objects/coordinates.py` ✅ **COMPLETED**
  - **File**: `src/domain/value_objects/timestamp.py` ✅ **COMPLETED**
  - **File**: `src/domain/value_objects/file_path.py` ✅ **COMPLETED**
  - **Reason**: Encapsulate simple data with validation
  - **Impact**: Prevents invalid data and improves code clarity

#### 2.3 Create Domain Events
- [x] **Create `src/domain/events/`** directory ✅ **COMPLETED**
  - **File**: `src/domain/events/screenshot_captured.py` ✅ **COMPLETED**
  - **File**: `src/domain/events/monitoring_started.py` ✅ **COMPLETED**
  - **File**: `src/domain/events/system_events.py` ✅ **COMPLETED**
  - **Reason**: Enable decoupled communication between domains
  - **Impact**: Improves extensibility and maintainability

#### 2.4 Create Service Interfaces
- [x] **Create `src/domain/interfaces/`** directory ✅ **COMPLETED**
  - **File**: `src/domain/interfaces/screenshot_service.py` ✅ **COMPLETED**
  - **File**: `src/domain/interfaces/monitoring_service.py` ✅ **COMPLETED**
  - **File**: `src/domain/interfaces/analysis_service.py` ✅ **COMPLETED**
  - **File**: `src/domain/interfaces/storage_service.py` ✅ **COMPLETED**
  - **File**: `src/domain/interfaces/event_service.py` ✅ **COMPLETED**
  - **Reason**: Define clear contracts for business services
  - **Impact**: Enables dependency inversion and better testing

#### 2.5 Create Application Services
- [x] **Create `src/application/services/`** directory ✅ **COMPLETED**
  - **File**: `src/application/services/screenshot_service.py` ✅ **COMPLETED**
  - **File**: `src/application/services/monitoring_service.py` ✅ **COMPLETED**
  - **File**: `src/application/services/analysis_service.py` ✅ **COMPLETED**
  - **Reason**: Centralize business logic and reduce coupling
  - **Impact**: Simplifies testing and maintenance

### 3. Repository Pattern Implementation
**Priority**: 🟡 **High**  
**Timeline**: Phase 2.2 (Days 4-5)

#### 3.1 Create Repository Interfaces
- [x] **Create `src/domain/repositories/`** directory ✅ **COMPLETED**
  - **File**: `src/domain/repositories/screenshot_repository.py` ✅ **COMPLETED**
  - **File**: `src/domain/repositories/configuration_repository.py` ✅ **COMPLETED**
  - **File**: `src/domain/repositories/monitoring_repository.py` ✅ **COMPLETED**
  - **Reason**: Abstract data access from business logic
  - **Impact**: Enables different storage implementations

#### 3.2 Implement Repository Classes
- [x] **Create `src/infrastructure/repositories/`** directory ✅ **COMPLETED**
  - **File**: `src/infrastructure/repositories/file_screenshot_repository.py` ✅ **COMPLETED**
  - **File**: `src/infrastructure/repositories/memory_screenshot_repository.py` ✅ **COMPLETED**
  - **File**: `src/infrastructure/repositories/json_configuration_repository.py` ✅ **COMPLETED**
  - **Reason**: Provide concrete implementations for data access
  - **Impact**: Separates persistence concerns from business logic

### 4. Dependency Injection Container
**Priority**: 🟡 **High**  
**Timeline**: Phase 2.3 (Days 6-7)

#### 4.1 Create DI Container
- [x] **Create `src/infrastructure/dependency_injection/`** directory ✅ **COMPLETED**
  - **File**: `src/infrastructure/dependency_injection/container.py` ✅ **COMPLETED**
  - **File**: `src/infrastructure/dependency_injection/bindings.py` ✅ **COMPLETED**
  - **Reason**: Manage object creation and dependencies
  - **Impact**: Enables loose coupling and easier testing

#### 4.2 Update Application Entry Point
- [ ] **Modify `main.py`**
  - **Change**: Replace manual object creation with DI container
  - **Reason**: Centralize dependency management
  - **Impact**: Simplified application startup and configuration

## Code Refactoring

### 1. API Layer Refactoring
**Priority**: 🔴 **Critical**  
**Timeline**: Phase 2.4 (Days 8-10)  
**Status**: ✅ **COMPLETE**

#### 1.1 Extract API Controllers
- [x] **Create `src/interfaces/controllers/`** directory
  - **File**: `src/interfaces/controllers/screenshot_controller.py` ✅
  - **File**: `src/interfaces/controllers/monitoring_controller.py` ✅
  - **File**: `src/interfaces/controllers/analysis_controller.py` ✅
  - **File**: `src/interfaces/controllers/configuration_controller.py` ✅
  - **Reason**: Separate HTTP concerns from business logic
  - **Impact**: Cleaner API handlers and better testability

#### 1.2 Refactor Server Class
- [x] **Modify `src/api/server.py`**
  - **Current Issues**: God object with mixed responsibilities (600+ lines)
  - **Changes**: 
    - Extract route handling to controllers ✅
    - Simplify to HTTP server only ✅
    - Remove business logic ✅
  - **Reason**: Single Responsibility Principle violation
  - **Impact**: Easier to maintain and test

#### 1.3 Create Request/Response Models
- [x] **Create `src/interfaces/dto/`** directory
  - **File**: `src/interfaces/dto/screenshot_dto.py` ✅
  - **File**: `src/interfaces/dto/monitoring_dto.py` ✅
  - **File**: `src/interfaces/dto/analysis_dto.py` ✅
  - **File**: `src/interfaces/dto/configuration_dto.py` ✅
  - **File**: `src/interfaces/dto/common_dto.py` ✅
  - **Reason**: Type-safe API contracts
  - **Impact**: Better validation and documentation

### 2. Storage Layer Refactoring
**Priority**: 🟡 **High**  
**Timeline**: Phase 2.5 (Days 11-12)  
**Status**: ✅ **COMPLETE**

#### 2.1 Simplify Storage Manager
- [x] **Refactor `src/core/storage/storage_manager.py`**
  - **Current Issues**: Complex interface with 474 lines
  - **Changes**:
    - Extract storage strategies to separate classes ✅
    - Implement factory pattern for storage selection ✅
    - Remove business logic ✅
  - **Reason**: Reduces complexity and improves maintainability
  - **Impact**: Easier to add new storage backends

#### 2.2 Refactor Screenshot Manager
- [x] **Refactor `src/core/storage/screenshot_manager_unified.py`**
  - **Current Issues**: God object with 514 lines, mixed responsibilities
  - **Changes**:
    - Extract business logic to service layer ✅
    - Keep only data access operations ✅
    - Simplify interface ✅
  - **Reason**: Single Responsibility Principle violation
  - **Impact**: Better separation of concerns

### 3. Monitoring Layer Refactoring
**Priority**: 🟡 **High**  
**Timeline**: Phase 2.6 (Days 13-14)

#### 3.1 Simplify ROI Monitor
- [x] **Refactor `src/core/monitoring/roi_monitor.py`** ✅ **COMPLETE**
  - **Current Issues**: Mixed monitoring and business logic (209 lines)
  - **Changes**:
    - Extract change detection algorithms
    - Implement strategy pattern for detection methods
    - Use events for communication
  - **Reason**: Improves extensibility and testability
  - **Impact**: Easier to add new detection algorithms
  - **Status**: ✅ Created RefactoredROIMonitor with strategy pattern and events

#### 3.2 Create Change Detection Strategies
- [x] **Create `src/infrastructure/monitoring/`** directory ✅ **COMPLETE**
  - **File**: `src/infrastructure/monitoring/threshold_detector.py` ✅
  - **File**: `src/infrastructure/monitoring/pixel_diff_detector.py` ✅
  - **File**: `src/infrastructure/monitoring/hash_comparison_detector.py` ✅
  - **File**: `src/infrastructure/monitoring/change_detection_context.py` ✅
  - **File**: `src/infrastructure/monitoring/strategy_factory.py` ✅
  - **Reason**: Pluggable detection algorithms
  - **Impact**: Better performance tuning and extensibility
  - **Status**: ✅ All strategies implemented with interface compliance

### 4. Configuration Refactoring
**Priority**: 🟡 **Medium**  
**Timeline**: Phase 2.7 (Days 15-16)

#### 4.1 Simplify Configuration Manager
- [ ] **Refactor `src/core/config/config.py`**
  - **Current Issues**: Mixed concerns (191 lines)
  - **Changes**:
    - Extract validation logic
    - Implement configuration sources hierarchy
    - Add type safety
  - **Reason**: Improves maintainability and validation
  - **Impact**: Better error handling and extensibility

#### 4.2 Create Configuration Validators
- [ ] **Create `src/infrastructure/configuration/`** directory
  - **File**: `src/infrastructure/configuration/validators.py`
  - **File**: `src/infrastructure/configuration/sources.py`
  - **File**: `src/infrastructure/configuration/mergers.py`
  - **Reason**: Separate validation and merging logic
  - **Impact**: Better error messages and type safety

### 5. Capture Layer Refactoring
**Priority**: 🟢 **Medium**  
**Timeline**: Phase 2.8 (Days 17-18)

#### 5.1 Simplify Capture Manager
- [x] **Refactor `src/core/capture/screenshot_capture.py`** ✅
  - **Current Issues**: Complex fallback logic
  - **Changes**:
    - Implement chain of responsibility pattern ✅
    - Extract platform-specific implementations ✅
    - Improve error handling ✅
  - **Reason**: Better maintainability and extensibility
  - **Impact**: Easier to add new capture methods
  - **Status**: Created RefactoredCaptureManager with chain of responsibility

#### 5.2 Extract Platform Implementations
- [x] **Create `src/infrastructure/capture/`** directory ✅
  - **File**: `src/infrastructure/capture/windows_capture.py` ✅
  - **File**: `src/infrastructure/capture/linux_capture.py` ✅
  - **File**: `src/infrastructure/capture/wsl_capture.py` ✅
  - **File**: `src/infrastructure/capture/platform_detector.py` ✅
  - **File**: `src/infrastructure/capture/capture_chain.py` ✅
  - **File**: `src/infrastructure/capture/refactored_capture_manager.py` ✅
  - **Reason**: Platform-specific optimizations
  - **Impact**: Better performance and maintainability
  - **Status**: Complete platform-specific implementation with chain pattern

## Redundancy Removal

### 1. Duplicate Screenshot Managers
**Priority**: 🔴 **Critical**  
**Timeline**: Phase 2.9 (Day 19)

#### 1.1 Remove Duplicate Files
- [x] **Delete `src/core/capture/screenshot_capture_refactored.py`** ✅
  - **Reason**: Duplicate of `screenshot_capture.py` with identical functionality
  - **Justification**: Both files implement `ScreenshotCaptureManager` class with same methods
  - **Impact**: Reduces confusion and maintenance overhead

#### 1.2 Consolidate Storage Implementations
- [ ] **Analysis: `src/core/storage/storage_manager.py` vs other storage files**
  - **Action**: Keep unified approach, remove obsolete implementations
  - **Reason**: Multiple storage abstractions serving same purpose
  - **Impact**: Simplified storage architecture

### 2. Empty Placeholder Directories
**Priority**: 🟢 **Low**  
**Timeline**: Phase 2.9 (Day 19)

#### 2.1 Remove Empty Modules
- [x] **Remove `src/models/` directory** ✅
  - **Reason**: Empty directory with only `__init__.py`
  - **Justification**: Functionality moved to domain entities
  - **Impact**: Cleaner project structure

- [x] **Remove `src/services/` directory** ✅
  - **Reason**: Empty directory with only `__init__.py`
  - **Justification**: Functionality moved to application services
  - **Impact**: Cleaner project structure

- [x] **Remove `src/ui/` directory** ✅
  - **Reason**: Empty directory, UI is in static/templates
  - **Justification**: No backend UI components needed
  - **Impact**: Cleaner project structure

### 3. Redundant Configuration Files
**Priority**: 🟡 **Medium**  
**Timeline**: Phase 2.9 (Day 19)

#### 3.1 Consolidate Configuration
- [x] **Analysis: `src/screen_agent_config.json` vs `config/screen_agent_config.json`** ✅
  - **Action**: Keep single configuration location (`config/screen_agent_config.json`)
  - **Reason**: Duplicate configuration files cause confusion
  - **Impact**: Simplified configuration management

### 4. Unused Utility Functions
**Priority**: 🟢 **Low**  
**Timeline**: Phase 2.10 (Day 20)

#### 4.1 Audit Utility Functions ✅
- [x] **Review `src/utils/platform_detection.py`** ✅
  - **Action**: Kept for legacy compatibility (used by main.py and tests)
  - **Reason**: New platform detector exists in infrastructure layer
  - **Impact**: Both systems co-exist during transition

- [x] **Review `src/utils/keyboard_handler.py`** ✅
  - **Action**: Kept in utils for legacy compatibility (used by main.py)
  - **Reason**: Main.py still uses legacy architecture
  - **Impact**: Will be moved to infrastructure in future phases

## Implementation Order

### Phase 2.1: Foundation (Days 1-3)
1. Create domain models and entities
2. Create service interfaces
3. Set up new directory structure

### Phase 2.2: Repository Layer (Days 4-5)
1. Implement repository interfaces
2. Create repository implementations
3. Update storage abstractions

### Phase 2.3: Dependency Injection (Days 6-7)
1. Create DI container
2. Update application entry point
3. Configure service bindings

### Phase 2.4: API Layer (Days 8-10) ✅ **COMPLETE**
1. Extract controllers from server ✅
2. Create request/response DTOs ✅
3. Refactor server class ✅

### Phase 2.5: Storage Refactoring (Days 11-12) ✅ **COMPLETE**
1. Simplify storage manager ✅
2. Refactor screenshot manager ✅
3. Update storage interfaces ✅

### Phase 2.6: Monitoring Refactoring (Days 13-14) ✅ **COMPLETE**
1. Simplify ROI monitor ✅
2. Create detection strategies ✅
3. Implement event-driven monitoring ✅

### Phase 2.7: Configuration Refactoring (Days 15-16) ✅
1. Simplify configuration manager ✅
2. Create validators and sources ✅
3. Improve type safety ✅

### Phase 2.8: Capture Refactoring (Days 17-18) ✅
1. Simplify capture manager ✅
2. Extract platform implementations ✅
3. Improve error handling ✅

### Phase 2.9: Redundancy Removal (Day 19) ✅
1. Remove duplicate files ✅
2. Remove empty directories ✅
3. Consolidate configurations ✅

### Phase 2.10: Final Cleanup (Day 20) ✅
1. Audit utility functions ✅ 
2. Update imports and dependencies ✅
3. Final testing and validation ✅

## Testing Strategy

### 1. Unit Testing Approach
- [ ] **Create test structure**: `tests/unit/` for each module
- [ ] **Mock external dependencies**: Use dependency injection for mocking
- [ ] **Test business logic**: Focus on service layer testing
- [ ] **Test domain models**: Validate entity behavior and constraints

### 2. Integration Testing
- [ ] **API endpoint testing**: Test controller behavior
- [ ] **Storage integration**: Test repository implementations
- [ ] **Monitoring workflows**: Test end-to-end monitoring flows
- [ ] **Configuration loading**: Test configuration management

### 3. Testing Tools Setup
- [ ] **Configure pytest**: Set up test runner and fixtures
- [ ] **Add test dependencies**: Mock libraries and test utilities
- [ ] **Create test data**: Sample screenshots and configurations
- [ ] **Set up test database**: In-memory storage for testing

## Risk Assessment

### High Risk Areas 🔴
1. **Main Application Entry Point**: Changes to `main.py` could break startup
2. **API Server Refactoring**: Risk of breaking existing endpoints
3. **Storage Migration**: Risk of data loss during storage refactoring
4. **Configuration Changes**: Risk of breaking existing configuration files

### Medium Risk Areas 🟡
1. **Dependency Injection**: Complexity of managing object lifecycles
2. **Event System Integration**: Risk of event handling issues
3. **Platform-Specific Code**: Risk of breaking platform compatibility
4. **Repository Pattern**: Risk of performance degradation

### Low Risk Areas 🟢
1. **Domain Model Creation**: New code with minimal impact
2. **Utility Function Changes**: Limited scope and impact
3. **Test Code Addition**: No impact on production code
4. **Documentation Updates**: No functional impact

### Mitigation Strategies
1. **Incremental Implementation**: Make changes in small, testable increments
2. **Backward Compatibility**: Maintain existing interfaces during transition
3. **Comprehensive Testing**: Test each change thoroughly before proceeding
4. **Rollback Plan**: Keep ability to revert changes if issues arise
5. **Configuration Backup**: Backup existing configuration before changes

## Success Criteria

### Technical Metrics
- [ ] **Code Coverage**: Achieve >80% test coverage
- [ ] **Cyclomatic Complexity**: Reduce average complexity by 30%
- [ ] **Code Duplication**: Eliminate identified duplicate code
- [ ] **Dependency Coupling**: Reduce coupling metrics by 40%

### Functional Verification
- [ ] **All APIs Working**: Verify all existing endpoints function correctly
- [ ] **Screenshot Capture**: Verify manual and automatic capture works
- [ ] **ROI Monitoring**: Verify monitoring start/stop functionality
- [ ] **AI Analysis**: Verify AI integration remains functional
- [ ] **Configuration**: Verify settings can be saved and loaded

### Performance Verification
- [ ] **Response Times**: Maintain or improve API response times
- [ ] **Memory Usage**: No significant increase in memory consumption
- [ ] **Storage Performance**: Maintain or improve storage operations
- [ ] **Monitoring Performance**: No degradation in monitoring responsiveness

---

**Phase 2 Complete**: Detailed refactoring plan ready for implementation approval.

**Next Step**: Await approval to proceed to Phase 3 - Implementation and Cleanup
