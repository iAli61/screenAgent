import threading
from datetime import datetime
from platform_detection import WSL_MODE

# Keyboard handling setup
KEYBOARD_AVAILABLE = False
TRIGGER_KEY = 'f12'

def setup_keyboard():
    """Initialize keyboard shortcuts if available"""
    global KEYBOARD_AVAILABLE
    if WSL_MODE:
        print("Keyboard shortcuts not available in WSL mode")
        return False
    
    try:
        import keyboard
        KEYBOARD_AVAILABLE = True
        print(f"Keyboard shortcuts enabled. Press '{TRIGGER_KEY}' to take a screenshot.")
        return True
    except ImportError as e:
        print(f"Keyboard module not available: {e}")
        print("Run with sudo for keyboard shortcuts or use web interface.")
        return False

def start_keyboard_listener(screenshot_callback):
    """Start listening for keyboard events to trigger screenshots
    
    Args:
        screenshot_callback: Function to call when trigger key is pressed
    """
    if not KEYBOARD_AVAILABLE:
        print("Keyboard shortcuts not available")
        return
    
    try:
        import keyboard
        
        def on_trigger_key():
            try:
                new_screenshot = screenshot_callback()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"Key-triggered screenshot taken at {timestamp}")
                return timestamp, new_screenshot
            except Exception as e:
                print(f"Error in keyboard trigger: {e}")
                return None, None
        
        keyboard.add_hotkey(TRIGGER_KEY, on_trigger_key)
        print(f"Keyboard listener active. Press '{TRIGGER_KEY}' to take a screenshot.")
        
        # Return the listening thread
        keyboard_thread = threading.Thread(target=lambda: keyboard.wait('esc'), daemon=True)
        return keyboard_thread
    
    except Exception as e:
        print(f"Failed to initialize keyboard listener: {e}")
        print("Keyboard shortcuts will not be available.")
        return None