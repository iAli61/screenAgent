"""
API endpoint tests for Screenshot operations
"""
import pytest
import json
from unittest.mock import patch


class TestScreenshotEndpoints:
    """Test screenshot API endpoints"""
    
    def test_get_screenshots_success(self, client, api_headers):
        """Test GET /api/screenshots/screenshots returns success"""
        response = client.get('/api/screenshots/screenshots', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'screenshots' in data
        assert 'total_count' in data
        assert isinstance(data['screenshots'], list)
    
    def test_get_screenshots_with_pagination(self, client, api_headers):
        """Test GET /api/screenshots/screenshots with pagination parameters"""
        response = client.get('/api/screenshots/screenshots?limit=10&offset=5', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_get_screenshots_with_session_filter(self, client, api_headers):
        """Test GET /api/screenshots/screenshots with session_id filter"""
        response = client.get('/api/screenshots/screenshots?session_id=test-session', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_trigger_screenshot_success(self, client, api_headers):
        """Test POST /api/screenshots/take captures screenshot"""
        payload = {'metadata': {'test': 'data'}}
        response = client.post('/api/screenshots/take', 
                              data=json.dumps(payload), 
                              headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'screenshot_id' in data
    
    def test_trigger_screenshot_no_content_type(self, client):
        """Test POST /api/screenshots/take without content-type header"""
        response = client.post('/api/screenshots/take')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_trigger_screenshot_empty_json(self, client, api_headers):
        """Test POST /api/screenshots/take with empty JSON"""
        response = client.post('/api/screenshots/take', 
                              data='{}', 
                              headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_get_preview_success(self, client):
        """Test GET /api/screenshots/preview returns image data"""
        response = client.get('/api/screenshots/preview')
        
        assert response.status_code == 200
        assert response.mimetype == 'image/png'
        assert response.headers['Cache-Control'] == 'no-cache'
        assert response.headers['Content-Type'] == 'image/png'
        assert response.data == b'fake-image-data'
    
    def test_head_preview_success(self, client):
        """Test HEAD /api/screenshots/preview returns headers without body"""
        response = client.head('/api/screenshots/preview')
        
        # Should return 200 with proper headers but no body
        assert response.status_code == 200
        assert response.data == b''
    
    def test_delete_all_screenshots(self, client, api_headers):
        """Test DELETE /api/screenshots/screenshots deletes all screenshots"""
        response = client.delete('/api/screenshots/screenshots', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'message' in data
    
    def test_options_request(self, client):
        """Test OPTIONS requests are handled correctly"""
        response = client.options('/api/screenshots/screenshots')
        
        # OPTIONS should be allowed without authentication
        assert response.status_code in [200, 204]


class TestScreenshotErrorHandling:
    """Test error handling for screenshot endpoints"""
    
    @patch('src.api.blueprints.screenshots.get_container')
    def test_controller_exception_handling(self, mock_get_container, client, api_headers):
        """Test handling of controller exceptions"""
        from src.domain.exceptions.screenshot_exceptions import ScreenshotException
        
        # Mock controller to raise exception
        mock_controller = mock_get_container.return_value.get.return_value
        mock_controller.get_screenshots.side_effect = ScreenshotException("Test error")
        
        response = client.get('/api/screenshots/screenshots', headers=api_headers)
        
        # Should handle exception gracefully
        assert response.status_code in [400, 500]
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_invalid_json_handling(self, client):
        """Test handling of invalid JSON in request body"""
        headers = {'Content-Type': 'application/json'}
        response = client.post('/api/screenshots/take', 
                              data='invalid json', 
                              headers=headers)
        
        # Should handle invalid JSON gracefully
        assert response.status_code in [400, 422]


class TestScreenshotCompatibility:
    """Test compatibility with existing frontend expectations"""
    
    def test_response_format_compatibility(self, client, api_headers):
        """Test that response format matches frontend expectations"""
        response = client.get('/api/screenshots/screenshots', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check required fields for frontend compatibility
        required_fields = ['success', 'screenshots', 'total_count']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are present for frontend compatibility"""
        response = client.get('/api/screenshots/screenshots')
        
        # Check for CORS headers
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        for header in cors_headers:
            assert header in response.headers, f"Missing CORS header: {header}"
    
    def test_security_headers_present(self, client):
        """Test that security headers are present"""
        response = client.get('/api/screenshots/screenshots')
        
        security_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection'
        ]
        
        for header in security_headers:
            assert header in response.headers, f"Missing security header: {header}"
