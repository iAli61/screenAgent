#!/usr/bin/env python3
"""
Modern test suite for ScreenAgent using clean architecture
Tests dependency injection, services, and core functionality
"""
import sys
import os
import asyncio
import traceback
from pathlib import Path

# Add the project root directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.append(os.path.join(project_root, 'src'))


class ModernScreenAgentTest:
    """Test suite for the clean architecture implementation"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.container = None
    
    def print_header(self, title: str):
        """Print a test section header"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print('='*60)
    
    def test_result(self, test_name: str, success: bool, error: str = None):
        """Record test result"""
        if success:
            print(f"✅ {test_name} - PASSED")
            self.tests_passed += 1
        else:
            print(f"❌ {test_name} - FAILED: {error}")
            self.tests_failed += 1
    
    def test_imports(self):
        """Test that all clean architecture imports work"""
        self.print_header("Testing Clean Architecture Imports")
        
        # Test core config (using new DI approach)
        try:
            from src.infrastructure.dependency_injection.container import get_container, setup_container
            self.test_result("Core Config (DI) Import", True)
        except Exception as e:
            self.test_result("Core Config (DI) Import", False, str(e))
        
        # Test dependency injection
        try:
            from src.infrastructure.dependency_injection import get_container, setup_container
            self.test_result("Dependency Injection Import", True)
        except Exception as e:
            self.test_result("Dependency Injection Import", False, str(e))
        
        # Test domain interfaces
        try:
            from src.domain.interfaces.screenshot_service import IScreenshotService
            from src.domain.interfaces.monitoring_service import IMonitoringService
            from src.domain.interfaces.analysis_service import IAnalysisService
            self.test_result("Domain Interfaces Import", True)
        except Exception as e:
            self.test_result("Domain Interfaces Import", False, str(e))
        
        # Test application services
        try:
            from src.application.services.screenshot_service import ScreenshotService
            from src.application.services.monitoring_service import MonitoringService
            from src.application.services.analysis_service import AnalysisService
            self.test_result("Application Services Import", True)
        except Exception as e:
            self.test_result("Application Services Import", False, str(e))
        
        # Test controllers
        try:
            from src.interfaces.controllers.screenshot_controller import ScreenshotController
            from src.interfaces.controllers.monitoring_controller import MonitoringController
            from src.interfaces.controllers.analysis_controller import AnalysisController
            self.test_result("Controllers Import", True)
        except Exception as e:
            self.test_result("Controllers Import", False, str(e))
    
    def test_dependency_injection(self):
        """Test dependency injection container"""
        self.print_header("Testing Dependency Injection Container")
        
        try:
            from src.infrastructure.dependency_injection import setup_container
            from src.utils.platform_detection import is_wsl, is_windows, is_linux_with_display
            
            # Detect platform
            if is_wsl():
                platform_name = "wsl"
            elif is_windows():
                platform_name = "windows"  
            elif is_linux_with_display():
                platform_name = "linux"
            else:
                platform_name = "unknown"
            
            # Setup container
            config_dict = {
                "storage": {
                    "type": "memory",  # Use memory for testing
                    "base_path": "test_screenshots"
                },
                "monitoring": {
                    "default_strategy": "threshold",
                    "threshold": 30
                },
                "capture": {
                    "platform": platform_name,
                    "wsl_enabled": is_wsl()
                }
            }
            
            self.container = setup_container(config_dict)
            self.test_result("DI Container Setup", True)
            
        except Exception as e:
            self.test_result("DI Container Setup", False, str(e))
            traceback.print_exc()
    
    def test_service_resolution(self):
        """Test that services can be resolved from container"""
        self.print_header("Testing Service Resolution")
        
        if not self.container:
            self.test_result("Service Resolution", False, "Container not initialized")
            return
        
        try:
            from src.domain.interfaces.screenshot_service import IScreenshotService
            from src.domain.interfaces.monitoring_service import IMonitoringService
            from src.domain.interfaces.analysis_service import IAnalysisService
            from src.infrastructure.storage.storage_factory import StorageManager
            
            # Test service resolution
            screenshot_service = self.container.get(IScreenshotService)
            self.test_result("Screenshot Service Resolution", True)
            
            monitoring_service = self.container.get(IMonitoringService)
            self.test_result("Monitoring Service Resolution", True)
            
            analysis_service = self.container.get(IAnalysisService)
            self.test_result("Analysis Service Resolution", True)
            
            storage_manager = self.container.get(StorageManager)
            self.test_result("Storage Manager Resolution", True)
            
        except Exception as e:
            self.test_result("Service Resolution", False, str(e))
            traceback.print_exc()
    
    async def test_screenshot_service(self):
        """Test screenshot service functionality"""
        self.print_header("Testing Screenshot Service")
        
        if not self.container:
            self.test_result("Screenshot Service Test", False, "Container not initialized")
            return
        
        try:
            from src.domain.interfaces.screenshot_service import IScreenshotService
            
            screenshot_service = self.container.get(IScreenshotService)
            
            # Test basic functionality (without actually taking screenshots in test)
            self.test_result("Screenshot Service Instantiation", True)
            
        except Exception as e:
            self.test_result("Screenshot Service Test", False, str(e))
            traceback.print_exc()
    
    async def test_controllers(self):
        """Test controller functionality"""
        self.print_header("Testing Controllers")
        
        if not self.container:
            self.test_result("Controllers Test", False, "Container not initialized")
            return
        
        try:
            from src.interfaces.controllers.screenshot_controller import ScreenshotController
            from src.interfaces.controllers.monitoring_controller import MonitoringController
            from src.interfaces.controllers.analysis_controller import AnalysisController
            from src.domain.interfaces.screenshot_service import IScreenshotService
            from src.domain.interfaces.monitoring_service import IMonitoringService
            from src.domain.interfaces.analysis_service import IAnalysisService
            
            # Get services from container
            screenshot_service = self.container.get(IScreenshotService)
            monitoring_service = self.container.get(IMonitoringService)
            analysis_service = self.container.get(IAnalysisService)
            
            # Test controller creation
            screenshot_controller = ScreenshotController(screenshot_service, analysis_service)
            self.test_result("Screenshot Controller Creation", True)
            
            monitoring_controller = MonitoringController(monitoring_service, screenshot_service)
            self.test_result("Monitoring Controller Creation", True)
            
            analysis_controller = AnalysisController(analysis_service, screenshot_service)
            self.test_result("Analysis Controller Creation", True)
            
        except Exception as e:
            self.test_result("Controllers Test", False, str(e))
            traceback.print_exc()
    
    def test_flask_app_initialization(self):
        """Test Flask app can be initialized"""
        self.print_header("Testing Flask App Initialization")
        
        try:
            from src.api.flask_app import create_app
            
            # Test Flask app creation
            app = create_app()
            self.test_result("Flask App Initialization", True)
            
        except Exception as e:
            self.test_result("Flask App Initialization", False, str(e))
            traceback.print_exc()
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🎯 ScreenAgent Clean Architecture Test Suite")
        print("=" * 60)
        
        # Synchronous tests
        self.test_imports()
        self.test_dependency_injection()
        self.test_service_resolution()
        self.test_flask_app_initialization()
        
        # Asynchronous tests
        await self.test_screenshot_service()
        await self.test_controllers()
        
        # Print summary
        print(f"\n📊 Test Summary:")
        print(f"✅ Passed: {self.tests_passed}")
        print(f"❌ Failed: {self.tests_failed}")
        print(f"📈 Success Rate: {(self.tests_passed / (self.tests_passed + self.tests_failed) * 100):.1f}%")
        
        if self.tests_failed == 0:
            print("\n🎉 All tests passed! Clean architecture is working correctly.")
            return True
        else:
            print(f"\n⚠️  {self.tests_failed} test(s) failed. Please check the errors above.")
            return False


async def main():
    """Main test function"""
    test_suite = ModernScreenAgentTest()
    success = await test_suite.run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        traceback.print_exc()
        sys.exit(1)
