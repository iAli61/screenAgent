#!/usr/bin/env python3
"""
ScreenAgent Installation Script
Handles dependency installation with better error handling
"""
import subprocess
import sys
import os

def run_pip_install(package, description=""):
    """Install a package with pip and handle errors gracefully"""
    try:
        print(f"📦 Installing {package}...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package
        ], capture_output=True, text=True, check=True)
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}")
        if description:
            print(f"   {description}")
        print(f"   Error: {e.stderr.strip()}")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is already installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} already installed")
        return True
    except ImportError:
        return False

def install_core_dependencies():
    """Install core dependencies required for basic functionality"""
    print("🔧 Installing core dependencies...")
    
    core_packages = [
        ("numpy>=1.24.0", "Required for image processing and calculations"),
        ("Pillow>=9.0.0", "Required for image handling and screenshot processing"),
    ]
    
    success_count = 0
    for package, description in core_packages:
        if run_pip_install(package, description):
            success_count += 1
    
    return success_count == len(core_packages)

def install_screenshot_dependencies():
    """Install screenshot capture dependencies"""
    print("\n📸 Installing screenshot dependencies...")
    
    # Try pyautogui first (works on most systems)
    if not check_package("pyautogui"):
        if run_pip_install("pyautogui>=0.9.53", "Recommended for cross-platform screenshot capture"):
            print("✅ PyAutoGUI installed - screenshot functionality ready")
            return True
    else:
        print("✅ Screenshot functionality already available")
        return True
    
    # If pyautogui fails, try mss (Linux alternative)
    print("⚠️  PyAutoGUI installation failed, trying MSS as alternative...")
    if run_pip_install("mss>=6.1.0", "Alternative screenshot library for Linux"):
        print("✅ MSS installed - screenshot functionality ready")
        return True
    
    print("❌ Could not install any screenshot library")
    print("   You may need to install system dependencies first:")
    print("   Ubuntu/Debian: sudo apt-get install python3-tk python3-dev")
    print("   Fedora/RHEL: sudo dnf install tkinter python3-devel")
    return False

def install_optional_dependencies():
    """Install optional dependencies for enhanced features"""
    print("\n🔧 Installing optional dependencies...")
    
    optional_packages = [
        ("python-dotenv>=0.19.0", "dotenv", "Support for .env configuration files"),
        ("keyboard>=0.13.5", "keyboard", "Keyboard shortcuts (may require root on Linux)"),
    ]
    
    for package, import_name, description in optional_packages:
        if not check_package(import_name):
            run_pip_install(package, description)

def install_ai_dependencies():
    """Install AI integration dependencies"""
    print("\n🤖 Installing AI dependencies (optional)...")
    
    # OpenAI
    if not check_package("openai"):
        if run_pip_install("openai>=1.0.0", "OpenAI API integration for screenshot analysis"):
            print("✅ OpenAI integration available")
    
    # Azure AI (beta version)
    print("\nℹ️  Azure AI integration is currently in beta.")
    install_azure = input("Install Azure AI integration? (y/N): ").lower().strip()
    if install_azure in ['y', 'yes']:
        if not check_package("azure"):
            run_pip_install("azure-ai-inference>=1.0.0b9", "Azure AI integration (beta)")

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ is required")
        return False
    
    if version.major == 3 and version.minor >= 12:
        print("ℹ️  Using Python 3.12+ - some packages may need newer versions")
    
    print("✅ Python version is compatible")
    return True

def main():
    """Main installation process"""
    print("🎯 ScreenAgent Installation")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install core dependencies
    if not install_core_dependencies():
        print("\n❌ Failed to install core dependencies")
        print("Please check the error messages above and resolve any issues.")
        sys.exit(1)
    
    # Install screenshot dependencies
    if not install_screenshot_dependencies():
        print("\n⚠️  Screenshot functionality may not work properly")
        print("ScreenAgent can still run but won't be able to capture screenshots.")
    
    # Install optional dependencies
    install_optional_dependencies()
    
    # Ask about AI dependencies
    print("\n🤖 AI Integration")
    install_ai = input("Install AI dependencies for screenshot analysis? (Y/n): ").lower().strip()
    if install_ai not in ['n', 'no']:
        install_ai_dependencies()
    
    print("\n" + "=" * 40)
    print("✅ Installation completed!")
    print("\nNext steps:")
    print("1. Run: python main.py")
    print("2. Open: http://localhost:8000")
    print("3. Configure your ROI and start monitoring!")
    
    # Check if we can run the basic test
    print("\n🧪 Testing basic functionality...")
    try:
        if os.path.exists("test_basic.py"):
            subprocess.run([sys.executable, "test_basic.py"], check=False)
        elif os.path.exists("minimal_test.py"):
            subprocess.run([sys.executable, "minimal_test.py"], check=False)
    except Exception as e:
        print(f"Could not run test: {e}")

if __name__ == "__main__":
    main()
