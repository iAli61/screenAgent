#!/usr/bin/env python3
"""
Test script for Azure OpenAI configuration
"""
import os
import dotenv
import sys

# Load environment variables from .env file
dotenv.load_dotenv()

def check_azure_config():
    """Check Azure OpenAI configuration"""
    print("==== Azure OpenAI Configuration Check ====")
    
    # Check essential environment variables
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_base = os.getenv("AZURE_API_BASE")
    api_version = os.getenv("AZURE_API_VERSION", "2025-01-01-preview")
    
    print(f"AZURE_API_BASE: {'Set' if api_base else 'MISSING'}")
    print(f"AZURE_OPENAI_API_KEY: {'Set' if api_key else 'MISSING'}")
    print(f"AZURE_API_VERSION: {api_version}")
    
    # Check LLM settings
    llm_enabled = os.getenv("LLM_ENABLED", "").lower() == "true"
    llm_model = os.getenv("LLM_MODEL", "gpt-4o")
    
    print(f"LLM_ENABLED: {llm_enabled}")
    print(f"LLM_MODEL: {llm_model}")
    
    # Display instructions based on findings
    print("\n==== Diagnostic Results ====")
    missing = []
    if not api_key:
        missing.append("AZURE_OPENAI_API_KEY")
    if not api_base:
        missing.append("AZURE_API_BASE")
    
    if missing:
        print("PROBLEM: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease add the following to your .env file:")
        for var in missing:
            print(f"{var}=your_{var.lower()}_here")
            
    if not llm_enabled:
        print("\nNOTE: LLM functionality is disabled. Add LLM_ENABLED=true to your .env file to enable it.")
        
    # Everything looks good
    if not missing and llm_enabled:
        print("Your Azure OpenAI configuration appears to be set correctly.")
        print("If you're still experiencing issues, please check that:")
        print("1. Your API key is valid")
        print("2. Your endpoint URL is correct")
        print("3. The model deployment name is correct and available in your Azure resource")

if __name__ == "__main__":
    check_azure_config()
