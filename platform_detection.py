import os
import sys

def is_wsl():
    """Detect if running in Windows Subsystem for Linux"""
    if os.path.exists('/proc/version'):
        with open('/proc/version', 'r') as f:
            if "microsoft" in f.read().lower():
                print("Running in WSL environment")
                return True
    return False

# Global environment flags
WSL_MODE = is_wsl()