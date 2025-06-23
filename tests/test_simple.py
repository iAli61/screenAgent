#!/usr/bin/env python3
"""
Simple test to verify the clean architecture works
"""
import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)
sys.path.append(os.path.join(project_root, 'src'))

print("Testing clean architecture components...")

try:
    from src.infrastructure.dependency_injection.container import get_container, setup_container
    print("✅ Configuration (DI) import successful")
except ImportError as e:
    print(f"❌ Configuration (DI) import failed: {e}")

try:
    from src.infrastructure.dependency_injection import get_container, setup_container
    print("✅ Dependency injection import successful")
except ImportError as e:
    print(f"❌ Dependency injection import failed: {e}")

try:
    from src.domain.interfaces.screenshot_service import IScreenshotService
    from src.domain.interfaces.monitoring_service import IMonitoringService
    print("✅ Domain interfaces import successful")
except ImportError as e:
    print(f"❌ Domain interfaces import failed: {e}")

try:
    from src.application.services.screenshot_service import ScreenshotService
    print("✅ Application services import successful")
except ImportError as e:
    print(f"❌ Application services import failed: {e}")

try:
    from src.interfaces.controllers.screenshot_controller import ScreenshotController
    print("✅ Controllers import successful")
except ImportError as e:
    print(f"❌ Controllers import failed: {e}")

try:
    from src.api.flask_app import create_app
    print("✅ Flask app import successful")
except ImportError as e:
    print(f"❌ Flask app import failed: {e}")

print("Basic import test completed.")
