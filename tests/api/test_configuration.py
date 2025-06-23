"""
API endpoint tests for Configuration operations
"""
import pytest
import json
from unittest.mock import patch


class TestConfigurationEndpoints:
    """Test configuration API endpoints"""
    
    def test_health_check_success(self, client):
        """Test GET /api/config/health returns health status"""
        response = client.get('/api/config/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data
        assert 'checks' in data
        assert data['status'] == 'ok'
    
    def test_get_status_success(self, client):
        """Test GET /api/config/status returns system status"""
        response = client.get('/api/config/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'status' in data
        assert 'components' in data
        assert 'timestamp' in data
    
    def test_get_config_success(self, client, api_headers):
        """Test GET /api/config/get returns configuration"""
        response = client.get('/api/config/get', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'config' in data
    
    def test_update_config_success(self, client, api_headers):
        """Test POST /api/config/set updates configuration"""
        payload = {
            'key': 'test_setting',
            'value': 'test_value'
        }
        response = client.post('/api/config/set',
                              data=json.dumps(payload),
                              headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'message' in data
    
    def test_head_health_check(self, client):
        """Test HEAD /api/config/health works correctly"""
        response = client.head('/api/config/health')
        
        assert response.status_code == 200
        assert response.data == b''
    
    def test_head_status_check(self, client):
        """Test HEAD /api/config/status works correctly"""
        response = client.head('/api/config/status')
        
        assert response.status_code == 200
        assert response.data == b''


class TestConfigurationValidation:
    """Test configuration endpoint validation"""
    
    def test_invalid_config_key(self, client, api_headers):
        """Test setting configuration with invalid key"""
        payload = {
            'key': '',  # Empty key should be invalid
            'value': 'test_value'
        }
        response = client.post('/api/config/set',
                              data=json.dumps(payload),
                              headers=api_headers)
        
        # Should handle validation error
        assert response.status_code in [400, 422]
    
    def test_missing_required_fields(self, client, api_headers):
        """Test setting configuration with missing required fields"""
        payload = {
            'value': 'test_value'  # Missing 'key' field
        }
        response = client.post('/api/config/set',
                              data=json.dumps(payload),
                              headers=api_headers)
        
        # Should handle missing field error
        assert response.status_code in [400, 422]


class TestConfigurationErrorHandling:
    """Test error handling for configuration endpoints"""
    
    @patch('src.api.blueprints.configuration.get_container')
    def test_controller_exception_handling(self, mock_get_container, client):
        """Test handling of controller exceptions"""
        from src.domain.exceptions.configuration_exceptions import ConfigurationException
        
        # Mock controller to raise exception
        mock_controller = mock_get_container.return_value.get.return_value
        mock_controller.get_health.side_effect = ConfigurationException("Database error")
        
        response = client.get('/api/config/health')
        
        # Should handle exception gracefully
        assert response.status_code in [400, 500]
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data


class TestConfigurationSecurity:
    """Test security aspects of configuration endpoints"""
    
    def test_health_endpoint_no_auth_required(self, client):
        """Test that health endpoint doesn't require authentication"""
        response = client.get('/api/config/health')
        
        # Health check should always be accessible
        assert response.status_code == 200
    
    def test_status_endpoint_no_auth_required(self, client):
        """Test that status endpoint doesn't require authentication"""
        response = client.get('/api/config/status')
        
        # Status check should always be accessible
        assert response.status_code == 200
    
    def test_sensitive_info_not_exposed(self, client):
        """Test that sensitive configuration is not exposed"""
        response = client.get('/api/config/get')
        
        if response.status_code == 200:
            data = json.loads(response.data)
            config = data.get('config', {})
            
            # Check that sensitive keys are not exposed
            sensitive_keys = ['password', 'secret', 'token', 'key']
            for key in config.keys():
                for sensitive in sensitive_keys:
                    if sensitive.lower() in key.lower():
                        # If sensitive key is present, value should be masked
                        assert config[key] in ['***', '[REDACTED]', '[HIDDEN]']


class TestConfigurationCompatibility:
    """Test compatibility with existing system expectations"""
    
    def test_health_response_format(self, client):
        """Test health endpoint response format matches expectations"""
        response = client.get('/api/config/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check required fields for health check
        required_fields = ['status', 'timestamp', 'checks']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Check status values
        assert data['status'] in ['ok', 'warning', 'error']
    
    def test_status_response_format(self, client):
        """Test status endpoint response format matches expectations"""
        response = client.get('/api/config/status')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check required fields for status
        required_fields = ['success', 'status', 'components']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
