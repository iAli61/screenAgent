"""
Service Bindings Configuration
Centralized configuration for dependency injection bindings
"""
from typing import Dict, Any
from pathlib import Path

from src.domain.interfaces.screenshot_service import IScreenshotService
from src.domain.interfaces.monitoring_service import IMonitoringService
from src.domain.interfaces.analysis_service import IAnalysisService
from src.domain.interfaces.capture_service import ICaptureService
from src.domain.repositories.screenshot_repository import IScreenshotRepository
from src.domain.repositories.configuration_repository import IConfigurationRepository

from src.application.services.screenshot_service import ScreenshotService
from src.application.services.monitoring_service import MonitoringService
from src.application.services.analysis_service import AnalysisService

from src.infrastructure.repositories.file_screenshot_repository import FileScreenshotRepository
from src.infrastructure.repositories.memory_screenshot_repository import MemoryScreenshotRepository
from src.infrastructure.repositories.json_configuration_repository import JsonConfigurationRepository
from src.infrastructure.capture.capture_service_impl import CaptureServiceImpl

# New storage infrastructure
from src.infrastructure.storage.storage_factory import StorageFactory, StorageManager
from src.infrastructure.storage.storage_strategy import IStorageFactory

# New monitoring infrastructure
from src.infrastructure.monitoring.strategy_factory import ChangeDetectionStrategyFactory
from src.infrastructure.monitoring.change_detection_context import ChangeDetectionContext
from src.domain.interfaces.change_detection_strategy import IChangeDetectionContext

from .container import DIContainer


class ServiceBindings:
    """Configuration for service bindings"""
    
    @staticmethod
    def configure_production(container: DIContainer, config: Dict[str, Any]):
        """Configure production service bindings"""
        
        # Repository bindings
        storage_config = config.get("storage", {})
        storage_type = storage_config.get("type", "file")
        
        if storage_type == "file":
            storage_dir = Path(storage_config.get("directory", "screenshots"))
            container.register_instance(
                IScreenshotRepository, 
                FileScreenshotRepository(storage_dir)
            )
        else:
            container.register_singleton(IScreenshotRepository, MemoryScreenshotRepository)
        
        # Configuration repository
        config_file = Path(config.get("config_file", "config/screen_agent_config.json"))
        container.register_instance(
            IConfigurationRepository,
            JsonConfigurationRepository(config_file)
        )
        
        # Storage infrastructure
        storage_config = config.get("storage", {})
        container.register_singleton(IStorageFactory, StorageFactory)
        
        # Create storage strategy based on config
        factory = StorageFactory()
        storage_strategy = factory.create_storage(
            storage_type=storage_config.get("type", "file"),
            base_path=storage_config.get("directory", "screenshots"),
            max_screenshots=storage_config.get("max_screenshots", 1000)
        )
        storage_manager = StorageManager(storage_strategy)
        container.register_instance(StorageManager, storage_manager)
        
        # Monitoring infrastructure
        monitoring_config = config.get("monitoring", {})
        default_strategy = monitoring_config.get("default_strategy", "threshold")
        detection_context = ChangeDetectionStrategyFactory.create_context_with_all_strategies()
        if default_strategy != "threshold":
            detection_context.switch_to_strategy(default_strategy)
        container.register_instance(IChangeDetectionContext, detection_context)
        
        # Capture service
        capture_service = CaptureServiceImpl()
        container.register_instance(ICaptureService, capture_service)
        
        # Application services
        container.register_singleton(IScreenshotService, ScreenshotService)
        container.register_singleton(IMonitoringService, MonitoringService)
        container.register_singleton(IAnalysisService, AnalysisService)
    
    @staticmethod
    def configure_development(container: DIContainer, config: Dict[str, Any]):
        """Configure development service bindings"""
        
        # Use file-based storage for development
        storage_dir = Path(config.get("storage", {}).get("directory", "dev_screenshots"))
        container.register_instance(
            IScreenshotRepository,
            FileScreenshotRepository(storage_dir)
        )
        
        # Development configuration
        config_file = Path("config/dev_config.json")
        container.register_instance(
            IConfigurationRepository,
            JsonConfigurationRepository(config_file)
        )
        
        # Storage infrastructure for development
        storage_config = config.get("storage", {})
        container.register_singleton(IStorageFactory, StorageFactory)
        
        factory = StorageFactory()
        storage_strategy = factory.create_storage(
            storage_type="file",
            base_path=storage_config.get("directory", "dev_screenshots"),
            max_screenshots=storage_config.get("max_screenshots", 100)
        )
        storage_manager = StorageManager(storage_strategy)
        container.register_instance(StorageManager, storage_manager)
        
        # Monitoring infrastructure for development
        monitoring_config = config.get("monitoring", {})
        default_strategy = monitoring_config.get("default_strategy", "threshold")
        detection_context = ChangeDetectionStrategyFactory.create_context_with_all_strategies()
        if default_strategy != "threshold":
            detection_context.switch_to_strategy(default_strategy)
        container.register_instance(IChangeDetectionContext, detection_context)
        
        # Capture service for development
        capture_service = CaptureServiceImpl()
        container.register_instance(ICaptureService, capture_service)
        
        # Application services
        container.register_singleton(IScreenshotService, ScreenshotService)
        container.register_singleton(IMonitoringService, MonitoringService)
        container.register_singleton(IAnalysisService, AnalysisService)
    
    @staticmethod
    def configure_testing(container: DIContainer, config: Dict[str, Any]):
        """Configure testing service bindings"""
        
        # Use in-memory repositories for testing
        container.register_singleton(IScreenshotRepository, MemoryScreenshotRepository)
        
        # Test configuration
        config_file = Path("test_config.json")
        container.register_instance(
            IConfigurationRepository,
            JsonConfigurationRepository(config_file)
        )
        
        # Storage infrastructure for testing (in-memory)
        container.register_singleton(IStorageFactory, StorageFactory)
        
        factory = StorageFactory()
        storage_strategy = factory.create_storage(
            storage_type="memory",
            max_screenshots=50
        )
        storage_manager = StorageManager(storage_strategy)
        container.register_instance(StorageManager, storage_manager)
        
        # Monitoring infrastructure for testing
        monitoring_config = config.get("monitoring", {})
        default_strategy = monitoring_config.get("default_strategy", "threshold")
        detection_context = ChangeDetectionStrategyFactory.create_context_with_all_strategies()
        if default_strategy != "threshold":
            detection_context.switch_to_strategy(default_strategy)
        container.register_instance(IChangeDetectionContext, detection_context)
        
        # Capture service for testing
        capture_service = CaptureServiceImpl()
        container.register_instance(ICaptureService, capture_service)
        
        # Application services
        container.register_singleton(IScreenshotService, ScreenshotService)
        container.register_singleton(IMonitoringService, MonitoringService)
        container.register_singleton(IAnalysisService, AnalysisService)


def get_binding_configuration(environment: str = "production") -> Dict[str, Any]:
    """Get binding configuration for specific environment"""
    
    base_config = {
        "storage": {
            "type": "file",
            "directory": "screenshots",
            "max_age_days": 30,
            "max_size_mb": 1000
        },
        "monitoring": {
            "default_threshold": 20.0,
            "default_interval": 0.5,
            "default_strategy": "threshold",
            "max_sessions": 10
        },
        "screenshot": {
            "default_format": "PNG",
            "quality": 95,
            "compression": "fast"
        }
    }
    
    if environment == "development":
        base_config.update({
            "storage": {
                **base_config["storage"],
                "directory": "dev_screenshots",
                "max_age_days": 7
            },
            "config_file": "config/dev_config.json"
        })
    
    elif environment == "testing":
        base_config.update({
            "storage": {
                **base_config["storage"],
                "type": "memory"
            },
            "config_file": "test_config.json"
        })
    
    elif environment == "production":
        base_config.update({
            "config_file": "config/screen_agent_config.json"
        })
    
    return base_config


def setup_environment_container(environment: str = "production") -> DIContainer:
    """Set up container for specific environment"""
    from .container import DIContainer
    
    container = DIContainer()
    config = get_binding_configuration(environment)
    
    if environment == "production":
        ServiceBindings.configure_production(container, config)
    elif environment == "development":
        ServiceBindings.configure_development(container, config)
    elif environment == "testing":
        ServiceBindings.configure_testing(container, config)
    else:
        raise ValueError(f"Unknown environment: {environment}")
    
    return container
