#!/usr/bin/env python3
"""
Test the updated analysis API with provider and model parameters
"""
import os
import requests
import json

# Set up environment variables for testing
os.environ['GITHUB_MODEL_TOKEN'] = 'test_token'
os.environ['AZURE_AI_MODELS'] = 'gpt-4o,gpt-4o-mini'
os.environ['GITHUB_MODELS'] = 'o3,o4-mini'

BASE_URL = "http://localhost:8000/api"

def test_analysis_api_with_providers():
    """Test the analysis API with different provider/model combinations"""
    print("🧪 Testing Analysis API with Provider/Model Parameters...")
    
    # Test cases with different provider/model combinations
    test_cases = [
        {
            "name": "GitHub Models with o4-mini",
            "data": {
                "screenshot_id": "test_screenshot_001",
                "prompt": "What do you see in this image?",
                "provider": "github",
                "model": "o4-mini"
            }
        },
        {
            "name": "GitHub Models with o3",
            "data": {
                "screenshot_id": "test_screenshot_002", 
                "prompt": "Analyze the UI elements in this screenshot",
                "provider": "github",
                "model": "o3"
            }
        },
        {
            "name": "Azure AI with gpt-4o",
            "data": {
                "screenshot_id": "test_screenshot_003",
                "prompt": "Describe the layout and content",
                "provider": "azure",
                "model": "gpt-4o"
            }
        },
        {
            "name": "Default provider/model",
            "data": {
                "screenshot_id": "test_screenshot_004",
                "prompt": "General analysis of this screenshot"
            }
        },
        {
            "name": "Invalid provider",
            "data": {
                "screenshot_id": "test_screenshot_005",
                "prompt": "Test with invalid provider",
                "provider": "invalid_provider",
                "model": "test_model"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🔍 {test_case['name']}")
        print(f"Request data: {json.dumps(test_case['data'], indent=2)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/analysis/analyze",
                json=test_case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Success!")
                print(f"Analysis ID: {result.get('analysis_id', 'N/A')}")
                
                # Handle the result field which might be None
                result_data = result.get('result') or {}
                print(f"Provider used: {result_data.get('provider', 'N/A')}")
                print(f"Model used: {result_data.get('model', 'N/A')}")
                print(f"LLM Status: {result_data.get('llm_status', 'N/A')}")
                print(f"Available Providers: {result_data.get('available_providers', [])}")
                
                if result_data.get('failure_reason'):
                    print(f"⚠️ Failure Reason: {result_data['failure_reason']}")
                
                # Show first 100 chars of analysis
                analysis = result_data.get('analysis', '')
                if analysis:
                    print(f"Analysis Preview: {analysis[:100]}...")
                    
                print(f"Raw response keys: {list(result.keys())}")
                if result_data:
                    print(f"Result data keys: {list(result_data.keys())}")
            else:
                print(f"❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error Details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"Raw Response: {response.text}")
                    
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("🚀 Testing Analysis API with Provider/Model Parameters")
    print("=" * 60)
    test_analysis_api_with_providers()
    print("\n✅ Analysis API tests completed!")
