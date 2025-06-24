#!/usr/bin/env python3
"""
Test script to verify the refactored LLM API functionality
"""
import os
import sys
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Add src to path so we can import our modules
sys.path.insert(0, 'src')

from api.llm_api import LLMAnalyzer

def test_llm_setup():
    """Test LLM client setup"""
    print("=== Testing LLM Setup ===")
    
    # Create config with LLM enabled
    config = {
        'llm_enabled': True,
        'llm_prompt': 'What is in this image?',
        'llm_model': os.getenv('LLM_MODEL', 'gpt-4o')
    }
    
    analyzer = LLMAnalyzer(config)
    
    print(f"LLM Enabled: {analyzer.llm_enabled}")
    print(f"Available providers: {analyzer.get_available_providers()}")
    print(f"Available models: {analyzer.get_available_models()}")
    print(f"Is available: {analyzer.is_available()}")
    
    return analyzer

def test_image_analysis(analyzer):
    """Test image analysis with the refactored methods"""
    print("\n=== Testing Image Analysis ===")
    
    # Test image path from your notebook
    image_path = 'screenshots/run_20250624_102302_c0ee4d92/images/region_91b32eaa-f938-499e-985b-7f73f40e4143.png'
    
    if not os.path.exists(image_path):
        print(f"Warning: Test image not found at {image_path}")
        return
    
    # Test encoding
    print("Testing image encoding...")
    base64_image = analyzer.encode_image(image_path)
    if base64_image:
        print(f"✅ Image encoded successfully (length: {len(base64_image)})")
    else:
        print("❌ Image encoding failed")
        return
    
    # Test analysis with Azure
    if 'azure' in analyzer.get_available_providers():
        print("\nTesting Azure analysis...")
        try:
            result = analyzer.analyze_image_from_path(
                image_path, 
                "What is in this image?", 
                provider='azure'
            )
            if result:
                print(f"✅ Azure analysis successful: {result[:100]}...")
            else:
                print("❌ Azure analysis returned None")
        except Exception as e:
            print(f"❌ Azure analysis error: {e}")
    
    # Test analysis with GitHub
    if 'github' in analyzer.get_available_providers():
        print("\nTesting GitHub analysis...")
        try:
            result = analyzer.analyze_image_from_path(
                image_path, 
                "What is in this image?", 
                provider='github'
            )
            if result:
                print(f"✅ GitHub analysis successful: {result[:100]}...")
            else:
                print("❌ GitHub analysis returned None")
        except Exception as e:
            print(f"❌ GitHub analysis error: {e}")

def main():
    """Main test function"""
    print("Testing refactored LLM API...")
    
    try:
        analyzer = test_llm_setup()
        
        if analyzer.is_available():
            test_image_analysis(analyzer)
        else:
            print("❌ LLM analyzer not available - check your configuration")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
