"""
API endpoint tests for Monitoring operations
"""
import pytest
import json
from unittest.mock import patch


class TestMonitoringEndpoints:
    """Test monitoring API endpoints"""
    
    def test_get_sessions_success(self, client, api_headers):
        """Test GET /api/monitoring/sessions returns sessions list"""
        response = client.get('/api/monitoring/sessions', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'sessions' in data
        assert 'total_count' in data
        assert isinstance(data['sessions'], list)
    
    def test_create_session_success(self, client, api_headers, sample_session_data):
        """Test POST /api/monitoring/sessions creates new session"""
        response = client.post('/api/monitoring/sessions',
                              data=json.dumps(sample_session_data),
                              headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'session_id' in data
    
    def test_get_session_by_id(self, client, api_headers):
        """Test GET /api/monitoring/sessions/{id} returns specific session"""
        session_id = 'test-session-123'
        response = client.get(f'/api/monitoring/sessions/{session_id}', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'session_id' in data
    
    def test_update_session_success(self, client, api_headers, sample_roi):
        """Test PUT /api/monitoring/sessions/{id} updates session"""
        session_id = 'test-session-123'
        update_data = {
            'roi': sample_roi,
            'interval': 2.0,
            'threshold': 0.2
        }
        
        response = client.put(f'/api/monitoring/sessions/{session_id}',
                             data=json.dumps(update_data),
                             headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_delete_session_success(self, client, api_headers):
        """Test DELETE /api/monitoring/sessions/{id} deletes session"""
        session_id = 'test-session-123'
        response = client.delete(f'/api/monitoring/sessions/{session_id}', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_start_session_success(self, client, api_headers):
        """Test POST /api/monitoring/sessions/{id}/start starts session"""
        session_id = 'test-session-123'
        response = client.post(f'/api/monitoring/sessions/{session_id}/start', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_stop_session_success(self, client, api_headers):
        """Test POST /api/monitoring/sessions/{id}/stop stops session"""
        session_id = 'test-session-123'
        response = client.post(f'/api/monitoring/sessions/{session_id}/stop', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_pause_session_success(self, client, api_headers):
        """Test POST /api/monitoring/sessions/{id}/pause pauses session"""
        session_id = 'test-session-123'
        response = client.post(f'/api/monitoring/sessions/{session_id}/pause', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_resume_session_success(self, client, api_headers):
        """Test DELETE /api/monitoring/sessions/{id}/pause resumes session"""
        session_id = 'test-session-123'
        response = client.delete(f'/api/monitoring/sessions/{session_id}/pause', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_get_session_screenshots(self, client, api_headers):
        """Test GET /api/monitoring/sessions/{id}/screenshots returns session screenshots"""
        session_id = 'test-session-123'
        response = client.get(f'/api/monitoring/sessions/{session_id}/screenshots', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # Response format depends on controller implementation
        assert response.content_type == 'application/json'


class TestMonitoringValidation:
    """Test monitoring endpoint validation"""
    
    def test_create_session_invalid_roi(self, client, api_headers):
        """Test creating session with invalid ROI data"""
        invalid_data = {
            'roi': {
                'x': -1,  # Invalid negative coordinate
                'y': 'invalid',  # Invalid type
                'width': 0,  # Invalid zero width
                'height': -100  # Invalid negative height
            }
        }
        
        response = client.post('/api/monitoring/sessions',
                              data=json.dumps(invalid_data),
                              headers=api_headers)
        
        # Should handle validation error
        assert response.status_code in [400, 422]
    
    def test_create_session_missing_roi(self, client, api_headers):
        """Test creating session without required ROI"""
        invalid_data = {
            'interval': 1.0,
            'threshold': 0.1
            # Missing 'roi' field
        }
        
        response = client.post('/api/monitoring/sessions',
                              data=json.dumps(invalid_data),
                              headers=api_headers)
        
        # Should handle missing required field
        assert response.status_code in [400, 422]
    
    def test_invalid_session_id_format(self, client, api_headers):
        """Test operations with invalid session ID format"""
        invalid_session_id = 'invalid-session-id-format-!@#$%'
        response = client.get(f'/api/monitoring/sessions/{invalid_session_id}', headers=api_headers)
        
        # Should handle invalid ID format
        assert response.status_code in [400, 404]


class TestMonitoringErrorHandling:
    """Test error handling for monitoring endpoints"""
    
    @patch('src.api.blueprints.monitoring.get_container')
    def test_controller_exception_handling(self, mock_get_container, client, api_headers):
        """Test handling of controller exceptions"""
        from src.domain.exceptions.monitoring_exceptions import MonitoringException
        
        # Mock controller to raise exception
        mock_controller = mock_get_container.return_value.get.return_value
        mock_controller.get_all_sessions.side_effect = MonitoringException("Session error")
        
        response = client.get('/api/monitoring/sessions', headers=api_headers)
        
        # Should handle exception gracefully
        assert response.status_code in [400, 500]
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_nonexistent_session_operations(self, client, api_headers):
        """Test operations on non-existent sessions"""
        nonexistent_id = 'nonexistent-session-999'
        
        # Test various operations on non-existent session
        operations = [
            ('GET', f'/api/monitoring/sessions/{nonexistent_id}'),
            ('PUT', f'/api/monitoring/sessions/{nonexistent_id}'),
            ('DELETE', f'/api/monitoring/sessions/{nonexistent_id}'),
            ('POST', f'/api/monitoring/sessions/{nonexistent_id}/start'),
            ('POST', f'/api/monitoring/sessions/{nonexistent_id}/stop')
        ]
        
        for method, url in operations:
            response = getattr(client, method.lower())(url, headers=api_headers)
            # Should return 404 or appropriate error
            assert response.status_code in [400, 404, 500]


class TestMonitoringWorkflow:
    """Test complete monitoring workflow scenarios"""
    
    def test_complete_session_lifecycle(self, client, api_headers, sample_session_data):
        """Test complete session lifecycle: create -> start -> pause -> resume -> stop -> delete"""
        # 1. Create session
        response = client.post('/api/monitoring/sessions',
                              data=json.dumps(sample_session_data),
                              headers=api_headers)
        assert response.status_code == 200
        session_data = json.loads(response.data)
        session_id = session_data.get('session_id', 'test-session')
        
        # 2. Start session
        response = client.post(f'/api/monitoring/sessions/{session_id}/start', headers=api_headers)
        assert response.status_code == 200
        
        # 3. Pause session
        response = client.post(f'/api/monitoring/sessions/{session_id}/pause', headers=api_headers)
        assert response.status_code == 200
        
        # 4. Resume session (DELETE pause)
        response = client.delete(f'/api/monitoring/sessions/{session_id}/pause', headers=api_headers)
        assert response.status_code == 200
        
        # 5. Stop session
        response = client.post(f'/api/monitoring/sessions/{session_id}/stop', headers=api_headers)
        assert response.status_code == 200
        
        # 6. Delete session
        response = client.delete(f'/api/monitoring/sessions/{session_id}', headers=api_headers)
        assert response.status_code == 200


class TestMonitoringCompatibility:
    """Test compatibility with existing system expectations"""
    
    def test_session_response_format(self, client, api_headers):
        """Test session response format matches frontend expectations"""
        response = client.get('/api/monitoring/sessions', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check required fields for frontend compatibility
        required_fields = ['success', 'sessions', 'total_count']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Sessions should be a list
        assert isinstance(data['sessions'], list)
    
    def test_roi_format_compatibility(self, client, api_headers, sample_session_data):
        """Test ROI format compatibility"""
        response = client.post('/api/monitoring/sessions',
                              data=json.dumps(sample_session_data),
                              headers=api_headers)
        
        assert response.status_code == 200
        # ROI format should be accepted by the API
        data = json.loads(response.data)
        assert data['success'] is True
