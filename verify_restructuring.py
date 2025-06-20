#!/usr/bin/env python3
"""
Final verification of restructured ScreenAgent codebase
Quick check of directory structure and basic module availability
"""
import os
import sys

def check_directory_structure():
    """Check that all expected directories exist"""
    print("📁 Checking Directory Structure:")
    
    expected_dirs = [
        'src/core/capture',
        'src/core/monitoring', 
        'src/core/storage',
        'src/core/events',
        'src/core/config',
        'src/utils',
        'src/services',
        'src/models',
        'src/api',
        'tests',
        'config',
        'docs',
        'scripts',
        'legacy'
    ]
    
    missing = []
    for dir_path in expected_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path}")
        else:
            print(f"   ❌ {dir_path} - MISSING")
            missing.append(dir_path)
    
    return len(missing) == 0

def check_key_files():
    """Check that key files are in expected locations"""
    print("\n📄 Checking Key Files:")
    
    key_files = [
        'src/core/capture/screenshot_capture_refactored.py',
        'src/core/monitoring/roi_monitor_refactored.py',
        'src/core/storage/storage_manager.py',
        'src/core/storage/screenshot_orchestrator.py',
        'src/core/events/events.py',
        'src/core/config/config.py',
        'src/utils/platform_detection.py',
        'docs/REFACTORING_TODO.md',
        'RESTRUCTURING_COMPLETE.md'
    ]
    
    missing = []
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - MISSING")
            missing.append(file_path)
    
    return len(missing) == 0

def check_init_files():
    """Check that __init__.py files exist for modules"""
    print("\n🔧 Checking Module Init Files:")
    
    init_files = [
        'src/__init__.py',
        'src/core/__init__.py',
        'src/core/capture/__init__.py',
        'src/core/monitoring/__init__.py',
        'src/core/storage/__init__.py',
        'src/core/events/__init__.py',
        'src/core/config/__init__.py',
        'src/utils/__init__.py',
        'src/services/__init__.py',
        'src/models/__init__.py',
        'tests/__init__.py'
    ]
    
    missing = []
    for init_file in init_files:
        if os.path.exists(init_file):
            print(f"   ✅ {init_file}")
        else:
            print(f"   ❌ {init_file} - MISSING")
            missing.append(init_file)
    
    return len(missing) == 0

def count_files_by_category():
    """Count files in each category"""
    print("\n📊 File Count Summary:")
    
    categories = {
        'Core Capture': 'src/core/capture',
        'Core Monitoring': 'src/core/monitoring',
        'Core Storage': 'src/core/storage', 
        'Core Events': 'src/core/events',
        'Core Config': 'src/core/config',
        'Utils': 'src/utils',
        'Tests': 'tests',
        'Docs': 'docs',
        'Scripts': 'scripts',
        'Legacy': 'legacy'
    }
    
    for category, directory in categories.items():
        if os.path.exists(directory):
            files = [f for f in os.listdir(directory) if f.endswith('.py')]
            print(f"   📦 {category}: {len(files)} Python files")
        else:
            print(f"   ❌ {category}: Directory missing")

def main():
    """Run all verification checks"""
    print("🔍 ScreenAgent Restructuring Verification")
    print("="*50)
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Key Files", check_key_files),
        ("Init Files", check_init_files)
    ]
    
    passed = 0
    failed = 0
    
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        print("-" * 30)
        
        if check_func():
            print(f"✅ {check_name} - PASSED")
            passed += 1
        else:
            print(f"❌ {check_name} - FAILED")
            failed += 1
    
    # Always show file count summary
    count_files_by_category()
    
    print("\n" + "="*50)
    print("📊 RESTRUCTURING VERIFICATION SUMMARY")
    print("="*50)
    print(f"✅ Checks Passed: {passed}")
    print(f"❌ Checks Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 RESTRUCTURING VERIFICATION SUCCESSFUL!")
        print("   All expected directories and files are in place.")
        print("   The modular architecture is properly organized.")
        print("   Ready for continued development.")
    else:
        print(f"\n⚠️  {failed} verification check(s) failed.")
        print("   Some files or directories may be missing.")
    
    print("="*50)
    return failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
