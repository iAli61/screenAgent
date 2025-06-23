"""
Pytest configuration and shared fixtures for ScreenAgent tests
"""
import pytest
import asyncio
import sys
from unittest.mock import Mock, AsyncMock

# Handle Flask app import with fallback
try:
    from src.api.flask_app import create_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    def create_app():
        """Fallback create_app for testing without Flask dependencies"""
        return None

try:
    from src.infrastructure.dependency_injection.container import get_container
except ImportError:
    def get_container():
        return Mock()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    if not FLASK_AVAILABLE:
        pytest.skip("Flask not available for testing")
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'testing-secret-key'
    
    # Disable security middleware for testing
    app.config['DISABLE_SECURITY'] = True
    
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the Flask application's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def mock_screenshot_controller():
    """Mock screenshot controller for testing."""
    controller = Mock()
    controller.get_screenshots = AsyncMock(return_value={
        'success': True,
        'screenshots': [],
        'total_count': 0,
        'offset': 0,
        'limit': None
    })
    controller.capture_full_screen = AsyncMock(return_value={
        'success': True,
        'screenshot_id': 'test-123',
        'message': 'Screenshot captured successfully'
    })
    controller.get_preview = AsyncMock(return_value=b'fake-image-data')
    controller.delete_all_screenshots = AsyncMock(return_value={
        'success': True,
        'message': 'All screenshots deleted'
    })
    return controller


@pytest.fixture
def mock_monitoring_controller():
    """Mock monitoring controller for testing."""
    controller = Mock()
    controller.get_all_sessions = AsyncMock(return_value={
        'success': True,
        'sessions': [],
        'total_count': 0
    })
    controller.create_session = AsyncMock(return_value={
        'success': True,
        'session_id': 'session-123',
        'message': 'Session created successfully'
    })
    controller.get_session = AsyncMock(return_value={
        'success': True,
        'session_id': 'session-123',
        'status': 'active'
    })
    controller.start_session = AsyncMock(return_value={
        'success': True,
        'message': 'Session started'
    })
    controller.stop_session = AsyncMock(return_value={
        'success': True,
        'message': 'Session stopped'
    })
    return controller


@pytest.fixture
def mock_configuration_controller():
    """Mock configuration controller for testing."""
    controller = Mock()
    controller.get_health = AsyncMock(return_value={
        'status': 'ok',
        'timestamp': '2025-06-23T16:30:00.000000',
        'checks': {
            'controller': 'ok',
            'repository': 'ok'
        },
        'response_time': 0.001
    })
    controller.get_status = AsyncMock(return_value={
        'success': True,
        'status': 'healthy',
        'timestamp': '2025-06-23T16:30:00.000000',
        'components': {
            'configuration': 'healthy',
            'storage': 'healthy',
            'api': 'healthy'
        }
    })
    controller.get_all_config = AsyncMock(return_value={
        'success': True,
        'config': {'test_key': 'test_value'},
        'count': 1
    })
    controller.update_config = AsyncMock(return_value={
        'success': True,
        'message': 'Configuration updated'
    })
    return controller


@pytest.fixture
def mock_analysis_controller():
    """Mock analysis controller for testing."""
    controller = Mock()
    controller.analyze_screenshot = AsyncMock(return_value={
        'success': True,
        'analysis_id': 'analysis-123',
        'result': 'Test analysis result'
    })
    controller.compare_screenshots = AsyncMock(return_value={
        'success': True,
        'comparison_id': 'comparison-123',
        'similarity_score': 0.95
    })
    return controller


@pytest.fixture(autouse=True)
def mock_di_container(monkeypatch, mock_screenshot_controller, mock_monitoring_controller, 
                     mock_configuration_controller, mock_analysis_controller):
    """Mock the DI container to return test controllers."""
    from src.interfaces.controllers.screenshot_controller import ScreenshotController
    from src.interfaces.controllers.monitoring_controller import MonitoringController
    from src.interfaces.controllers.configuration_controller import ConfigurationController
    from src.interfaces.controllers.analysis_controller import AnalysisController
    
    def mock_get_container():
        container = Mock()
        container.get = Mock(side_effect=lambda cls: {
            ScreenshotController: mock_screenshot_controller,
            MonitoringController: mock_monitoring_controller,
            ConfigurationController: mock_configuration_controller,
            AnalysisController: mock_analysis_controller
        }.get(cls, Mock()))
        return container
    
    monkeypatch.setattr('src.infrastructure.dependency_injection.container.get_container', mock_get_container)
    monkeypatch.setattr('src.api.blueprints.screenshots.get_container', mock_get_container)
    monkeypatch.setattr('src.api.blueprints.monitoring.get_container', mock_get_container)
    monkeypatch.setattr('src.api.blueprints.configuration.get_container', mock_get_container)
    monkeypatch.setattr('src.api.blueprints.analysis.get_container', mock_get_container)


@pytest.fixture
def api_headers():
    """Standard API headers for testing."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


@pytest.fixture
def sample_roi():
    """Sample ROI data for testing."""
    return {
        'x': 100,
        'y': 200,
        'width': 300,
        'height': 400
    }


@pytest.fixture
def sample_session_data(sample_roi):
    """Sample monitoring session data for testing."""
    return {
        'roi': sample_roi,
        'interval': 1.0,
        'threshold': 0.1
    }
