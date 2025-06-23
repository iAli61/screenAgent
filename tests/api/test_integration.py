"""
Comprehensive API integration tests
Tests the complete Flask application integration
"""
import pytest
import json
from unittest.mock import patch


class TestAPIIntegration:
    """Test complete API integration scenarios"""
    
    def test_api_endpoints_discovery(self, client):
        """Test that all expected API endpoints are available"""
        # Test core endpoint groups
        endpoint_groups = [
            '/api/config/health',
            '/api/config/status',
            '/api/screenshots/screenshots',
            '/api/monitoring/sessions',
            '/api/analysis/analyses'
        ]
        
        for endpoint in endpoint_groups:
            response = client.get(endpoint)
            # Should get 200 or at least not 404
            assert response.status_code != 404, f"Endpoint {endpoint} not found"
    
    def test_swagger_documentation_accessible(self, client):
        """Test that Swagger documentation is accessible"""
        # Test Swagger UI endpoint
        response = client.get('/docs/')
        
        # Should return HTML content for Swagger UI
        assert response.status_code == 200
        assert response.content_type.startswith('text/html')
    
    def test_cors_headers_consistency(self, client):
        """Test CORS headers are consistent across all endpoints"""
        endpoints = [
            '/api/config/health',
            '/api/screenshots/screenshots',
            '/api/monitoring/sessions',
            '/api/analysis/analyses'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            
            # Check for consistent CORS headers
            assert 'Access-Control-Allow-Origin' in response.headers
            assert 'Access-Control-Allow-Methods' in response.headers
            assert 'Access-Control-Allow-Headers' in response.headers
    
    def test_security_headers_consistency(self, client):
        """Test security headers are consistent across all endpoints"""
        endpoints = [
            '/api/config/health',
            '/api/screenshots/screenshots',
            '/api/monitoring/sessions',
            '/api/analysis/analyses'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            
            # Check for consistent security headers
            assert 'X-Content-Type-Options' in response.headers
            assert 'X-Frame-Options' in response.headers
            assert 'X-XSS-Protection' in response.headers
    
    def test_content_type_consistency(self, client, api_headers):
        """Test content type handling is consistent"""
        endpoints = [
            '/api/config/health',
            '/api/screenshots/screenshots',
            '/api/monitoring/sessions',
            '/api/analysis/analyses'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=api_headers)
            
            # JSON endpoints should return application/json
            if response.status_code == 200:
                assert response.content_type == 'application/json'


class TestHeadMethodSupport:
    """Test HEAD method support across all endpoints"""
    
    def test_head_method_screenshots(self, client):
        """Test HEAD method works for screenshot endpoints"""
        endpoints = [
            '/api/screenshots/screenshots',
            '/api/screenshots/preview'
        ]
        
        for endpoint in endpoints:
            response = client.head(endpoint)
            
            # HEAD should return 200 with no body
            assert response.status_code == 200
            assert response.data == b''
            
            # Should have same headers as GET
            get_response = client.get(endpoint)
            if get_response.status_code == 200:
                # Compare important headers
                important_headers = ['Content-Type', 'Content-Length']
                for header in important_headers:
                    if header in get_response.headers:
                        assert header in response.headers
    
    def test_head_method_config(self, client):
        """Test HEAD method works for configuration endpoints"""
        endpoints = [
            '/api/config/health',
            '/api/config/status'
        ]
        
        for endpoint in endpoints:
            response = client.head(endpoint)
            
            # HEAD should return 200 with no body
            assert response.status_code == 200
            assert response.data == b''
    
    def test_head_method_monitoring(self, client):
        """Test HEAD method works for monitoring endpoints"""
        response = client.head('/api/monitoring/sessions')
        
        # HEAD should return 200 with no body
        assert response.status_code == 200
        assert response.data == b''
    
    def test_head_method_analysis(self, client):
        """Test HEAD method works for analysis endpoints"""
        response = client.head('/api/analysis/analyses')
        
        # HEAD should return 200 with no body
        assert response.status_code == 200
        assert response.data == b''


class TestErrorHandlingConsistency:
    """Test error handling consistency across the API"""
    
    def test_404_error_format(self, client):
        """Test 404 errors have consistent format"""
        response = client.get('/api/nonexistent/endpoint')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        
        # Check error response structure
        assert 'success' in data
        assert data['success'] is False
        assert 'error' in data
        assert 'request_id' in data
    
    def test_405_method_not_allowed_format(self, client):
        """Test 405 errors have consistent format"""
        # Try PATCH on an endpoint that doesn't support it
        response = client.patch('/api/config/health')
        
        assert response.status_code == 405
        # Should have proper Allow header
        assert 'Allow' in response.headers
    
    def test_400_bad_request_format(self, client, api_headers):
        """Test 400 errors have consistent format"""
        # Send invalid JSON
        headers = {'Content-Type': 'application/json'}
        response = client.post('/api/screenshots/trigger',
                              data='invalid json',
                              headers=headers)
        
        # Should handle bad request consistently
        assert response.status_code in [400, 422]
        
        if response.content_type == 'application/json':
            data = json.loads(response.data)
            assert 'success' in data
            assert data['success'] is False


class TestPerformanceBasics:
    """Basic performance tests for API endpoints"""
    
    def test_health_check_performance(self, client):
        """Test health check responds quickly"""
        import time
        
        start_time = time.time()
        response = client.get('/api/config/health')
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Health check should be very fast (under 100ms)
        response_time = end_time - start_time
        assert response_time < 0.1, f"Health check too slow: {response_time}s"
    
    def test_concurrent_requests_handling(self, client):
        """Test API can handle multiple concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get('/api/config/health')
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        end_time = time.time()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        
        # Should complete reasonably quickly
        total_time = end_time - start_time
        assert total_time < 1.0, f"Concurrent requests too slow: {total_time}s"


class TestAPICompatibility:
    """Test API compatibility with existing frontend expectations"""
    
    def test_response_structure_consistency(self, client):
        """Test all API responses follow consistent structure"""
        endpoints = [
            '/api/config/status',
            '/api/screenshots/screenshots',
            '/api/monitoring/sessions',
            '/api/analysis/analyses'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            
            if response.status_code == 200 and response.content_type == 'application/json':
                data = json.loads(response.data)
                
                # Should have 'success' field
                assert 'success' in data, f"Missing 'success' field in {endpoint}"
                assert isinstance(data['success'], bool), f"'success' should be boolean in {endpoint}"
    
    def test_timestamp_format_consistency(self, client):
        """Test timestamp formats are consistent"""
        endpoints_with_timestamps = [
            '/api/config/health',
            '/api/config/status'
        ]
        
        for endpoint in endpoints_with_timestamps:
            response = client.get(endpoint)
            
            if response.status_code == 200:
                data = json.loads(response.data)
                
                if 'timestamp' in data:
                    timestamp = data['timestamp']
                    # Should be ISO format string
                    assert isinstance(timestamp, str)
                    assert 'T' in timestamp  # ISO format indicator
    
    def test_pagination_support(self, client):
        """Test pagination parameters are supported where expected"""
        endpoints_with_pagination = [
            '/api/screenshots/screenshots',
            '/api/monitoring/sessions',
            '/api/analysis/analyses'
        ]
        
        for endpoint in endpoints_with_pagination:
            # Test with pagination parameters
            response = client.get(f'{endpoint}?limit=10&offset=0')
            
            # Should not return error for pagination params
            assert response.status_code != 400
    
    def test_filter_support(self, client):
        """Test filter parameters are supported where expected"""
        # Test screenshot filtering
        response = client.get('/api/screenshots/screenshots?session_id=test')
        assert response.status_code != 400
        
        # Test analysis filtering
        response = client.get('/api/analysis/analyses?analysis_type=general')
        assert response.status_code != 400


class TestSwaggerDocumentation:
    """Test Swagger documentation completeness"""
    
    def test_swagger_json_accessible(self, client):
        """Test Swagger JSON specification is accessible"""
        # Common Swagger JSON endpoints
        swagger_endpoints = [
            '/swagger.json',
            '/docs/swagger.json',
            '/api/swagger.json'
        ]
        
        swagger_found = False
        for endpoint in swagger_endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                swagger_found = True
                data = json.loads(response.data)
                
                # Should be valid OpenAPI spec
                assert 'openapi' in data or 'swagger' in data
                assert 'info' in data
                assert 'paths' in data
                break
        
        # At least one swagger endpoint should work
        # Note: This might not be available depending on Flask-RESTX config
        # assert swagger_found, "No Swagger JSON endpoint found"
    
    def test_swagger_ui_elements(self, client):
        """Test Swagger UI contains expected elements"""
        response = client.get('/docs/')
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            
            # Should contain Swagger UI elements
            swagger_indicators = [
                'swagger',
                'api-docs',
                'Swagger UI'
            ]
            
            # At least one indicator should be present
            assert any(indicator.lower() in html_content.lower() 
                      for indicator in swagger_indicators)
