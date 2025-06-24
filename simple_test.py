#!/usr/bin/env python3
import os
import sys

# Add current directory to path
sys.path.insert(0, '/home/alibina/repo/screenAgent')

print("Testing LLM API refactor...")

try:
    print("1. Importing modules...")
    import base64
    from src.api.llm_api import LLMAnalyzer
    print("✅ Import successful")

    print("2. Creating analyzer...")
    config = {'llm_enabled': True}
    analyzer = LLMAnalyzer(config)
    print("✅ Analyzer created")

    print("3. Checking providers...")
    providers = analyzer.get_available_providers()
    print(f"✅ Available providers: {providers}")

    print("4. Testing image encoding...")
    image_path = '/home/alibina/repo/screenAgent/screenshots/run_20250624_102302_c0ee4d92/images/region_91b32eaa-f938-499e-985b-7f73f40e4143.png'
    if os.path.exists(image_path):
        encoded = analyzer.encode_image(image_path)
        if encoded:
            print(f"✅ Image encoding successful (length: {len(encoded)})")
        else:
            print("❌ Image encoding failed")
    else:
        print(f"⚠️  Test image not found: {image_path}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")
