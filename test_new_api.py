#!/usr/bin/env python3
"""
Test script for the new GitHub Models provider and updated analysis API
"""
import os
import requests
import json
from pathlib import Path

# Set up environment variables for testing
os.environ['GITHUB_MODEL_TOKEN'] = 'test_token'
os.environ['AZURE_AI_MODELS'] = 'gpt-4o,gpt-4o-mini'
os.environ['GITHUB_MODELS'] = 'o3,o4-mini'

BASE_URL = "http://localhost:8000/api"

def test_models_api():
    """Test the models API endpoints"""
    print("🧪 Testing Models API...")
    
    # Test getting all models
    response = requests.get(f"{BASE_URL}/models")
    print(f"GET /api/models: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test getting specific provider
    response = requests.get(f"{BASE_URL}/models/github")
    print(f"\nGET /api/models/github: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test getting Azure provider
    response = requests.get(f"{BASE_URL}/models/azure")
    print(f"\nGET /api/models/azure: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    # Test non-existent provider
    response = requests.get(f"{BASE_URL}/models/nonexistent")
    print(f"\nGET /api/models/nonexistent: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

def test_llm_analyzer():
    """Test the LLM analyzer directly"""
    print("\n🔬 Testing LLM Analyzer...")
    
    from src.api.llm_api import LLMAnalyzer
    
    analyzer = LLMAnalyzer({'llm_enabled': True})
    
    print("Available providers:", analyzer.get_available_providers())
    print("Available models:", analyzer.get_available_models())
    
    # Test with an image
    image_path = "screenshots/run_20250624_102302_c0ee4d92/images/region_91b32eaa-f938-499e-985b-7f73f40e4143.png"
    if Path(image_path).exists():
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Test with different providers
        for provider in analyzer.get_available_providers():
            print(f"\n🤖 Testing with provider: {provider}")
            try:
                result = analyzer.analyze_image(
                    image_data, 
                    custom_prompt="What do you see in this image?",
                    provider=provider
                )
                print(f"Result: {result[:100] if result else 'None'}...")
            except Exception as e:
                print(f"Error: {e}")

def test_analysis_api():
    """Test the updated analysis API with provider/model parameters"""
    print("\n📊 Testing Analysis API...")
    
    # This would require actual implementation in the analysis controller
    # For now, just show the structure
    analysis_request = {
        "screenshot_id": "test_screenshot",
        "prompt": "Describe what you see in this screenshot",
        "provider": "github",
        "model": "o4-mini"
    }
    
    print("Sample analysis request:")
    print(json.dumps(analysis_request, indent=2))

if __name__ == "__main__":
    print("🚀 Testing GitHub Models Integration")
    print("=" * 50)
    
    try:
        test_models_api()
        test_llm_analyzer()
        test_analysis_api()
        print("\n✅ All tests completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
