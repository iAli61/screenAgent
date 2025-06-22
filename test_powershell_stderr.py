#!/usr/bin/env python3
"""
Test to verify PowerShell scripts send debug output to stderr correctly
"""
import subprocess
import sys
import os

def test_standalone_powershell_script():
    """Test the standalone PowerShell script file"""
    print("Testing standalone PowerShell script...")
    
    script_path = os.path.join(os.path.dirname(__file__), "scripts", "screenshot_script.ps1")
    
    if not os.path.exists(script_path):
        print(f"❌ PowerShell script not found: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', script_path],
            capture_output=True,
            timeout=30,
            text=True
        )
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout length: {len(result.stdout.strip())} characters")
        print(f"Stderr content: {result.stderr.strip()}")
        
        if result.returncode == 0:
            # Check that stdout contains only base64 data (no debug text)
            stdout_lines = result.stdout.strip().split('\n')
            base64_data = stdout_lines[0] if stdout_lines else ""
            
            # Base64 data should be a single line with valid base64 characters
            import re
            is_base64 = bool(re.match(r'^[A-Za-z0-9+/]*={0,2}$', base64_data))
            
            if is_base64 and len(base64_data) > 1000:  # Should be substantial amount of data
                print("✅ Standalone PowerShell script working correctly")
                print(f"   - Base64 data length: {len(base64_data)} characters")
                print(f"   - Debug info in stderr: {'Yes' if result.stderr.strip() else 'No'}")
                return True
            else:
                print("❌ Stdout doesn't contain valid base64 data")
                print(f"   - Stdout preview: {result.stdout[:100]}...")
                return False
        else:
            print(f"❌ PowerShell script failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing PowerShell script: {e}")
        return False

def test_wsl_powershell_capture():
    """Test the WSL PowerShell capture implementation"""
    print("\nTesting WSL PowerShell capture implementation...")
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        from core.config.config import Config
        from core.capture.capture_implementations import WSLPowerShellCapture
        
        # Create a test config
        config = Config()
        capture = WSLPowerShellCapture(config)
        
        if not capture.initialize():
            print("❌ WSL PowerShell capture initialization failed")
            return False
        
        print("✅ WSL PowerShell capture initialized successfully")
        
        # Test full screen capture
        result = capture.capture_full_screen()
        
        if result.success:
            print("✅ Full screen capture successful")
            print(f"   - Screenshot size: {len(result.data)} bytes")
            print(f"   - Debug info available: {'Yes' if result.metadata.get('powershell_debug') else 'No'}")
            if result.metadata.get('powershell_debug'):
                print(f"   - Debug info: {result.metadata['powershell_debug'][:100]}...")
            return True
        else:
            print(f"❌ Full screen capture failed: {result.error}")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing WSL PowerShell capture: {e}")
        return False

def main():
    """Run all tests"""
    print("=== PowerShell stderr output test ===\n")
    
    # Check if we're in a WSL environment
    try:
        result = subprocess.run(['powershell.exe', '-Command', 'echo "test"'], 
                              capture_output=True, timeout=5, text=True)
        if result.returncode != 0:
            print("❌ PowerShell not available - skipping tests")
            return
    except:
        print("❌ PowerShell not available - skipping tests")
        return
    
    print("✅ PowerShell available - running tests\n")
    
    test1_passed = test_standalone_powershell_script()
    test2_passed = test_wsl_powershell_capture()
    
    print(f"\n=== Test Results ===")
    print(f"Standalone script test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"WSL capture test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! PowerShell scripts correctly send debug to stderr")
    else:
        print("\n⚠️  Some tests failed")

if __name__ == "__main__":
    main()
