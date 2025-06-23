"""
API endpoint tests for Analysis operations
"""
import pytest
import json
from unittest.mock import patch


class TestAnalysisEndpoints:
    """Test analysis API endpoints"""
    
    def test_get_analyses_success(self, client, api_headers):
        """Test GET /api/analysis/analyses returns analyses list"""
        response = client.get('/api/analysis/analyses', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'analyses' in data
        assert 'total_count' in data
        assert isinstance(data['analyses'], list)
    
    def test_get_analyses_with_filters(self, client, api_headers):
        """Test GET /api/analysis/analyses with filter parameters"""
        params = {
            'limit': '10',
            'offset': '5',
            'screenshot_id': 'test-screenshot-123',
            'analysis_type': 'general'
        }
        
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        response = client.get(f'/api/analysis/analyses?{query_string}', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_analyze_screenshot_success(self, client, api_headers):
        """Test POST /api/analysis/analyze performs screenshot analysis"""
        analysis_data = {
            'screenshot_id': 'test-screenshot-123',
            'analysis_type': 'general',
            'prompt': 'Analyze this screenshot'
        }
        
        response = client.post('/api/analysis/analyze',
                              data=json.dumps(analysis_data),
                              headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'analysis_id' in data
    
    def test_compare_screenshots_success(self, client, api_headers):
        """Test POST /api/analysis/compare compares screenshots"""
        comparison_data = {
            'screenshot1_id': 'test-screenshot-1',
            'screenshot2_id': 'test-screenshot-2',
            'comparison_type': 'similarity'
        }
        
        response = client.post('/api/analysis/compare',
                              data=json.dumps(comparison_data),
                              headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'comparison_id' in data
    
    def test_get_analysis_by_id_not_found(self, client, api_headers):
        """Test GET /api/analysis/analyses/{id} returns 404 for non-existent analysis"""
        analysis_id = 'nonexistent-analysis-123'
        response = client.get(f'/api/analysis/analyses/{analysis_id}', headers=api_headers)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Analysis' in data['message']
        assert 'not found' in data['message']
    
    def test_delete_analysis_not_found(self, client, api_headers):
        """Test DELETE /api/analysis/analyses/{id} returns 404 for non-existent analysis"""
        analysis_id = 'nonexistent-analysis-123'
        response = client.delete(f'/api/analysis/analyses/{analysis_id}', headers=api_headers)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'Analysis' in data['message']
        assert 'not found' in data['message']
    
    def test_text_extraction_not_implemented(self, client, api_headers):
        """Test POST /api/analysis/text-extraction returns 501 not implemented"""
        extraction_data = {
            'screenshot_id': 'test-screenshot-123',
            'roi': {'x': 100, 'y': 200, 'width': 300, 'height': 400}
        }
        
        response = client.post('/api/analysis/text-extraction',
                              data=json.dumps(extraction_data),
                              headers=api_headers)
        
        assert response.status_code == 501
        data = json.loads(response.data)
        assert 'not implemented' in data['message']
    
    def test_ui_elements_detection_not_implemented(self, client, api_headers):
        """Test POST /api/analysis/ui-elements returns 501 not implemented"""
        detection_data = {
            'screenshot_id': 'test-screenshot-123',
            'element_types': ['button', 'input', 'link']
        }
        
        response = client.post('/api/analysis/ui-elements',
                              data=json.dumps(detection_data),
                              headers=api_headers)
        
        assert response.status_code == 501
        data = json.loads(response.data)
        assert 'not implemented' in data['message']
    
    def test_change_detection_not_implemented(self, client, api_headers):
        """Test POST /api/analysis/change-detection returns 501 not implemented"""
        change_data = {
            'screenshot1_id': 'test-screenshot-1',
            'screenshot2_id': 'test-screenshot-2',
            'sensitivity': 0.1
        }
        
        response = client.post('/api/analysis/change-detection',
                              data=json.dumps(change_data),
                              headers=api_headers)
        
        assert response.status_code == 501
        data = json.loads(response.data)
        assert 'not implemented' in data['message']


class TestAnalysisValidation:
    """Test analysis endpoint validation"""
    
    def test_analyze_missing_screenshot_id(self, client, api_headers):
        """Test analysis with missing screenshot_id"""
        invalid_data = {
            'analysis_type': 'general',
            'prompt': 'Analyze this screenshot'
            # Missing 'screenshot_id'
        }
        
        response = client.post('/api/analysis/analyze',
                              data=json.dumps(invalid_data),
                              headers=api_headers)
        
        # Should handle missing required field
        assert response.status_code in [400, 422]
    
    def test_analyze_invalid_analysis_type(self, client, api_headers):
        """Test analysis with invalid analysis type"""
        invalid_data = {
            'screenshot_id': 'test-screenshot-123',
            'analysis_type': 'invalid_type',
            'prompt': 'Analyze this screenshot'
        }
        
        response = client.post('/api/analysis/analyze',
                              data=json.dumps(invalid_data),
                              headers=api_headers)
        
        # Should handle invalid analysis type
        assert response.status_code in [400, 422]
    
    def test_compare_missing_screenshots(self, client, api_headers):
        """Test comparison with missing screenshot IDs"""
        invalid_data = {
            'screenshot1_id': 'test-screenshot-1'
            # Missing 'screenshot2_id'
        }
        
        response = client.post('/api/analysis/compare',
                              data=json.dumps(invalid_data),
                              headers=api_headers)
        
        # Should handle missing required field
        assert response.status_code in [400, 422]
    
    def test_compare_same_screenshots(self, client, api_headers):
        """Test comparison with same screenshot ID for both images"""
        invalid_data = {
            'screenshot1_id': 'test-screenshot-1',
            'screenshot2_id': 'test-screenshot-1'  # Same as screenshot1_id
        }
        
        response = client.post('/api/analysis/compare',
                              data=json.dumps(invalid_data),
                              headers=api_headers)
        
        # Should handle identical screenshot IDs
        assert response.status_code in [400, 422]


class TestAnalysisErrorHandling:
    """Test error handling for analysis endpoints"""
    
    @patch('src.api.blueprints.analysis.get_container')
    def test_controller_exception_handling(self, mock_get_container, client, api_headers):
        """Test handling of controller exceptions"""
        # Mock controller to raise exception
        mock_controller = mock_get_container.return_value.get.return_value
        mock_controller.analyze_screenshot.side_effect = Exception("Analysis service error")
        
        analysis_data = {
            'screenshot_id': 'test-screenshot-123',
            'analysis_type': 'general'
        }
        
        response = client.post('/api/analysis/analyze',
                              data=json.dumps(analysis_data),
                              headers=api_headers)
        
        # Should handle exception gracefully
        assert response.status_code in [400, 500]
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
    
    def test_invalid_json_handling(self, client):
        """Test handling of invalid JSON in request body"""
        headers = {'Content-Type': 'application/json'}
        response = client.post('/api/analysis/analyze',
                              data='invalid json',
                              headers=headers)
        
        # Should handle invalid JSON gracefully
        assert response.status_code in [400, 422]


class TestAnalysisWorkflow:
    """Test complete analysis workflow scenarios"""
    
    def test_analyze_and_retrieve_workflow(self, client, api_headers):
        """Test complete workflow: analyze -> retrieve results"""
        # 1. Submit analysis request
        analysis_data = {
            'screenshot_id': 'test-screenshot-123',
            'analysis_type': 'general',
            'prompt': 'Describe what you see in this image'
        }
        
        response = client.post('/api/analysis/analyze',
                              data=json.dumps(analysis_data),
                              headers=api_headers)
        assert response.status_code == 200
        analysis_result = json.loads(response.data)
        analysis_id = analysis_result.get('analysis_id', 'test-analysis')
        
        # 2. Retrieve analysis results
        response = client.get(f'/api/analysis/analyses/{analysis_id}', headers=api_headers)
        # Expecting 404 since we have placeholder implementation
        assert response.status_code == 404
    
    def test_compare_workflow(self, client, api_headers):
        """Test screenshot comparison workflow"""
        # Submit comparison request
        comparison_data = {
            'screenshot1_id': 'test-screenshot-1',
            'screenshot2_id': 'test-screenshot-2',
            'comparison_type': 'pixel_diff'
        }
        
        response = client.post('/api/analysis/compare',
                              data=json.dumps(comparison_data),
                              headers=api_headers)
        assert response.status_code == 200
        comparison_result = json.loads(response.data)
        assert comparison_result['success'] is True
        assert 'comparison_id' in comparison_result
    
    def test_batch_analysis_scenario(self, client, api_headers):
        """Test scenario with multiple analysis requests"""
        screenshot_ids = ['screenshot-1', 'screenshot-2', 'screenshot-3']
        analysis_ids = []
        
        # Submit multiple analysis requests
        for screenshot_id in screenshot_ids:
            analysis_data = {
                'screenshot_id': screenshot_id,
                'analysis_type': 'general',
                'prompt': f'Analyze {screenshot_id}'
            }
            
            response = client.post('/api/analysis/analyze',
                                  data=json.dumps(analysis_data),
                                  headers=api_headers)
            assert response.status_code == 200
            result = json.loads(response.data)
            analysis_ids.append(result.get('analysis_id'))
        
        # Retrieve all analyses
        response = client.get('/api/analysis/analyses', headers=api_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestAnalysisCompatibility:
    """Test compatibility with existing system expectations"""
    
    def test_analyses_response_format(self, client, api_headers):
        """Test analyses list response format matches frontend expectations"""
        response = client.get('/api/analysis/analyses', headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check required fields for frontend compatibility
        required_fields = ['success', 'analyses', 'total_count']
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Analyses should be a list
        assert isinstance(data['analyses'], list)
    
    def test_analysis_result_format(self, client, api_headers):
        """Test analysis result format matches expectations"""
        analysis_data = {
            'screenshot_id': 'test-screenshot-123',
            'analysis_type': 'general'
        }
        
        response = client.post('/api/analysis/analyze',
                              data=json.dumps(analysis_data),
                              headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check expected fields in analysis response
        expected_fields = ['success', 'analysis_id']
        for field in expected_fields:
            assert field in data, f"Missing expected field: {field}"
    
    def test_comparison_result_format(self, client, api_headers):
        """Test comparison result format matches expectations"""
        comparison_data = {
            'screenshot1_id': 'test-screenshot-1',
            'screenshot2_id': 'test-screenshot-2'
        }
        
        response = client.post('/api/analysis/compare',
                              data=json.dumps(comparison_data),
                              headers=api_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check expected fields in comparison response
        expected_fields = ['success', 'comparison_id']
        for field in expected_fields:
            assert field in data, f"Missing expected field: {field}"
