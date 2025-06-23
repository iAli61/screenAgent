"""
Dependency Injection Container
Manages object creation and dependencies for the application
"""
import asyncio
from typing import Dict, Any, TypeVar, Type, Callable, Optional
from pathlib import Path
import logging

from src.domain.interfaces.screenshot_service import IScreenshotService
from src.domain.interfaces.monitoring_service import IMonitoringService
from src.domain.interfaces.analysis_service import IAnalysisService
from src.domain.interfaces.event_service import IEventService
from src.domain.interfaces.storage_service import IFileStorageService, IConfigurationService
from src.domain.interfaces.capture_service import ICaptureService
from src.domain.repositories.screenshot_repository import IScreenshotRepository
from src.domain.repositories.configuration_repository import IConfigurationRepository
from src.domain.repositories.monitoring_repository import IMonitoringRepository

from src.application.services.screenshot_service import ScreenshotService
from src.application.services.monitoring_service import MonitoringService
from src.application.services.analysis_service import AnalysisService

# Event services
from src.infrastructure.events.event_service import EventService

# Capture services
from src.infrastructure.capture.capture_service_impl import CaptureServiceImpl

from src.infrastructure.repositories.file_screenshot_repository import FileScreenshotRepository
from src.infrastructure.repositories.memory_screenshot_repository import MemoryScreenshotRepository
from src.infrastructure.repositories.json_configuration_repository import JsonConfigurationRepository
from src.infrastructure.repositories.memory_monitoring_repository import MemoryMonitoringRepository

# Storage infrastructure
from src.infrastructure.storage.storage_factory import StorageFactory, StorageManager
from src.infrastructure.storage.file_storage_service import FileStorageService

# Configuration infrastructure
from src.infrastructure.configuration import (
    ConfigurationValidator,
    ConfigurationSourceManager,
    SmartConfigurationMerger,
    FileConfigurationSource,
    EnvironmentConfigurationSource,
    DefaultConfigurationSource,
    RuntimeConfigurationSource
)
# Note: RefactoredConfigurationManager import removed to avoid circular dependency

# Monitoring infrastructure
from src.infrastructure.monitoring.change_detection_context import ChangeDetectionContext
from src.infrastructure.monitoring.threshold_detector import ThresholdDetector
from src.infrastructure.monitoring.pixel_diff_detector import PixelDiffDetector
from src.infrastructure.monitoring.hash_comparison_detector import HashComparisonDetector
from src.infrastructure.monitoring.strategy_factory import ChangeDetectionStrategyFactory

# Controllers
from src.interfaces.controllers.screenshot_controller import ScreenshotController
from src.interfaces.controllers.monitoring_controller import MonitoringController
from src.interfaces.controllers.analysis_controller import AnalysisController
from src.interfaces.controllers.configuration_controller import ConfigurationController


logger = logging.getLogger(__name__)
T = TypeVar('T')


class DIContainer:
    """Dependency injection container for service management"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
        self._singletons: Dict[Type, Any] = {}
        self._configuration: Dict[str, Any] = {}
        
    def configure(self, config: Dict[str, Any]):
        """Configure the container with application settings"""
        self._configuration = config
        logger.info("DI Container configured")
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]):
        """Register a singleton service"""
        self._services[interface] = implementation
        logger.debug(f"Registered singleton: {interface.__name__} -> {implementation.__name__}")
    
    def register_transient(self, interface: Type[T], factory: Callable[[], T]):
        """Register a transient service with factory"""
        self._factories[interface] = factory
        logger.debug(f"Registered transient: {interface.__name__}")
    
    def register_instance(self, interface: Type[T], instance: T):
        """Register a pre-created instance"""
        self._singletons[interface] = instance
        logger.debug(f"Registered instance: {interface.__name__}")
    
    def get(self, interface: Type[T]) -> T:
        """Get service instance"""
        # Check if instance already exists
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Check if it's a registered transient
        if interface in self._factories:
            return self._factories[interface]()
        
        # Check if it's a registered singleton
        if interface in self._services:
            # Create singleton instance
            implementation = self._services[interface]
            instance = self._create_instance(implementation)
            self._singletons[interface] = instance
            return instance
        
        raise ValueError(f"Service not registered: {interface.__name__}")
    
    def _create_instance(self, implementation: Type[T]) -> T:
        """Create instance with dependency injection"""
        # Get constructor parameters and inject dependencies
        # This is a simplified implementation - in a real scenario,
        # you'd use reflection to analyze constructor parameters
        
        if implementation == ScreenshotService:
            return implementation(
                file_storage=self.get(IFileStorageService),
                screenshot_repository=self.get(IScreenshotRepository),
                event_service=self.get(IEventService),
                capture_service=self.get(ICaptureService)
            )
        elif implementation == MonitoringService:
            return implementation(
                screenshot_service=self.get(IScreenshotService),
                analysis_service=self.get(IAnalysisService),
                session_repository=self.get(IMonitoringRepository),
                event_service=self.get(IEventService)
            )
        elif implementation == AnalysisService:
            return implementation(
                analysis_repository=None,  # TODO: Implement analysis repository
                event_service=self.get(IEventService)
            )
        elif implementation == FileScreenshotRepository:
            storage_dir = self._configuration.get("storage", {}).get("directory", "screenshots")
            return implementation(Path(storage_dir))
        elif implementation == MemoryScreenshotRepository:
            return implementation()
        elif implementation == JsonConfigurationRepository:
            config_file = self._configuration.get("config", {}).get("file", "config/screen_agent_config.json")
            return implementation(Path(config_file))
        elif implementation == ConfigurationValidator:
            return implementation()
        elif implementation == ConfigurationSourceManager:
            return implementation()
        elif implementation == SmartConfigurationMerger:
            return implementation()
        elif implementation == ChangeDetectionContext:
            return implementation()
        elif implementation == ChangeDetectionStrategyFactory:
            return implementation()
        elif implementation == ThresholdDetector:
            return implementation()
        elif implementation == PixelDiffDetector:
            return implementation()
        elif implementation == HashComparisonDetector:
            return implementation()
        else:
            # Default: try to create with no arguments
            return implementation()
    
    async def initialize_async_services(self):
        """Initialize services that require async setup"""
        # Initialize configuration repository first
        config_repo = self.get(IConfigurationRepository)
        if hasattr(config_repo, '_ensure_config_loaded'):
            await config_repo._ensure_config_loaded()
        
        logger.info("Async services initialized")
    
    def dispose(self):
        """Dispose of all services and clean up resources"""
        # Stop any background services
        for service in self._singletons.values():
            if hasattr(service, 'dispose'):
                service.dispose()
        
        self._singletons.clear()
        logger.info("DI Container disposed")


class ContainerBuilder:
    """Builder for setting up the DI container"""
    
    def __init__(self):
        self.container = DIContainer()
    
    def configure_default_services(self, config: Dict[str, Any]) -> 'ContainerBuilder':
        """Configure default service bindings"""
        self.container.configure(config)
        
        # Configuration infrastructure
        self.container.register_singleton(ConfigurationValidator, ConfigurationValidator)
        self.container.register_singleton(ConfigurationSourceManager, ConfigurationSourceManager)
        self.container.register_singleton(SmartConfigurationMerger, SmartConfigurationMerger)
        # Note: RefactoredConfigurationManager registration removed to avoid circular dependency
        
        # Monitoring infrastructure
        self.container.register_singleton(ChangeDetectionContext, ChangeDetectionContext)
        self.container.register_singleton(ChangeDetectionStrategyFactory, ChangeDetectionStrategyFactory)
        self.container.register_singleton(ThresholdDetector, ThresholdDetector)
        self.container.register_singleton(PixelDiffDetector, PixelDiffDetector)
        self.container.register_singleton(HashComparisonDetector, HashComparisonDetector)
        
        # Repository bindings
        storage_type = config.get("storage", {}).get("type", "file")
        if storage_type == "memory":
            self.container.register_singleton(IScreenshotRepository, MemoryScreenshotRepository)
        else:
            self.container.register_singleton(IScreenshotRepository, FileScreenshotRepository)
        
        self.container.register_singleton(IConfigurationRepository, JsonConfigurationRepository)
        
        # Monitoring repository (using memory implementation for now)
        self.container.register_singleton(IMonitoringRepository, MemoryMonitoringRepository)
        
        # Service bindings
        self.container.register_singleton(IScreenshotService, ScreenshotService)
        self.container.register_singleton(IMonitoringService, MonitoringService)
        self.container.register_singleton(IAnalysisService, AnalysisService)
        self.container.register_singleton(IEventService, EventService)
        
        # Capture service
        capture_service_instance = CaptureServiceImpl()
        self.container.register_instance(ICaptureService, capture_service_instance)
        
        # Storage infrastructure
        storage_factory = StorageFactory()
        storage_type = config.get("storage", {}).get("type", "file")
        base_path = config.get("storage", {}).get("base_path", "screenshots")
        
        if storage_type == "memory":
            storage_strategy = storage_factory.create_storage("memory")
        else:
            storage_strategy = storage_factory.create_storage("file", base_path=base_path)
        
        storage_manager = StorageManager(storage_strategy)
        self.container.register_instance(StorageManager, storage_manager)
        
        # File storage service using the same storage strategy
        file_storage_service = FileStorageService(storage_strategy)
        self.container.register_instance(IFileStorageService, file_storage_service)
        
        logger.info("Default services configured")
        return self
    
    def configure_testing_services(self) -> 'ContainerBuilder':
        """Configure services for testing"""
        config = {
            "storage": {"type": "memory"},
            "config": {"file": "test_config.json"}
        }
        
        self.container.configure(config)
        
        # Use in-memory implementations for testing
        self.container.register_singleton(IScreenshotRepository, MemoryScreenshotRepository)
        self.container.register_singleton(IConfigurationRepository, JsonConfigurationRepository)
        self.container.register_singleton(IMonitoringRepository, MemoryMonitoringRepository)
        
        # Service bindings
        self.container.register_singleton(IScreenshotService, ScreenshotService)
        self.container.register_singleton(IMonitoringService, MonitoringService)
        self.container.register_singleton(IAnalysisService, AnalysisService)
        self.container.register_singleton(IEventService, EventService)
        
        # Capture service for testing
        capture_service_instance = CaptureServiceImpl()
        self.container.register_instance(ICaptureService, capture_service_instance)
        
        # Storage infrastructure for testing
        storage_factory = StorageFactory()
        storage_strategy = storage_factory.create_storage("memory")
        storage_manager = StorageManager(storage_strategy)
        self.container.register_instance(StorageManager, storage_manager)
        
        # File storage service for testing
        file_storage_service = FileStorageService(storage_strategy)
        self.container.register_instance(IFileStorageService, file_storage_service)
        
        logger.info("Testing services configured")
        return self
    
    def build(self) -> DIContainer:
        """Build and return the configured container"""
        return self.container


# Global container instance
_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get the global DI container instance"""
    global _container
    if _container is None:
        raise RuntimeError("DI Container not initialized. Call setup_container() first.")
    return _container


def setup_container(config: Dict[str, Any]) -> DIContainer:
    """Set up the global DI container"""
    global _container
    
    builder = ContainerBuilder()
    _container = builder.configure_default_services(config).build()
    
    logger.info("Global DI Container set up")
    return _container


def setup_testing_container() -> DIContainer:
    """Set up the global DI container for testing"""
    global _container
    
    builder = ContainerBuilder()
    _container = builder.configure_testing_services().build()
    
    logger.info("Global testing DI Container set up")
    return _container


def dispose_container():
    """Dispose of the global DI container"""
    global _container
    if _container:
        _container.dispose()
        _container = None
    
    logger.info("Global DI Container disposed")
