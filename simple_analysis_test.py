#!/usr/bin/env python3
"""
Simple test to verify the analysis API with provider/model parameters
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def simple_test():
    print("🧪 Simple Analysis API Test with Provider/Model")
    
    test_data = {
        "screenshot_id": "test-screenshot-123", 
        "prompt": "What do you see in this image?",
        "provider": "github",
        "model": "o4-mini"
    }
    
    print("Request:")
    print(json.dumps(test_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/analysis/analyze",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nResponse:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    simple_test()
