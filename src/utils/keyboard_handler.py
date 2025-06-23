"""
Keyboard shortcut handler for ScreenAgent
"""
import threading
from typing import Optional, Callable


class KeyboardHandler:
    """Handles keyboard shortcuts for taking manual screenshots"""
    
    def __init__(self, screenshot_callback: Optional[Callable] = None):
        self.screenshot_callback = screenshot_callback
        self._keyboard_available = False
        self._keyboard_module = None
        self._running = False
        self._thread = None
        self._callback = None
        
        self._setup_keyboard()
    
    def initialize(self) -> bool:
        """Initialize the keyboard handler"""
        # Already initialized in __init__, just return the status
        return True
    
    def _setup_keyboard(self):
        """Setup keyboard monitoring if available"""
        try:
            # Import keyboard package if available
            import keyboard
            self._keyboard_module = keyboard
            self._keyboard_available = True
            print("⌨️  Keyboard shortcuts available")
        except ImportError:
            print("⚠️  Keyboard shortcuts not available (install 'keyboard' package)")
            self._keyboard_available = False
        except Exception as e:
            print(f"⚠️  Keyboard shortcuts not available: {e}")
            self._keyboard_available = False
    
    def is_available(self) -> bool:
        """Check if keyboard shortcuts are available"""
        return self._keyboard_available
    
    def start(self, shortcut: str = 'f12', callback: Callable = None):
        """Start listening for keyboard shortcuts"""
        if not self._keyboard_available or self._running:
            return None
        
        self._callback = callback or self._default_callback
        self._running = True
        
        try:
            # Setup the hotkey
            self._keyboard_module.add_hotkey(shortcut, self._on_hotkey)
            print(f"⌨️  Press {shortcut.upper()} to take a manual screenshot")
            
            # Start keyboard listener thread
            self._thread = threading.Thread(target=self._keyboard_loop, daemon=True)
            self._thread.start()
            
            return self._thread
            
        except Exception as e:
            print(f"Error setting up keyboard shortcut: {e}")
            self._running = False
            return None
    
    def stop(self):
        """Stop keyboard monitoring"""
        if self._running and self._keyboard_module:
            try:
                self._keyboard_module.unhook_all()
                self._running = False
                print("⌨️  Keyboard shortcuts stopped")
            except Exception as e:
                print(f"Error stopping keyboard handler: {e}")
    
    def _keyboard_loop(self):
        """Main keyboard listening loop"""
        try:
            while self._running:
                self._keyboard_module.wait()
        except Exception as e:
            print(f"Keyboard loop error: {e}")
    
    def _on_hotkey(self):
        """Handle hotkey press"""
        try:
            if self._callback:
                self._callback()
        except Exception as e:
            print(f"Error handling hotkey: {e}")
    
    def _default_callback(self):
        """Default callback for keyboard shortcuts"""
        try:
            print("📸 Keyboard shortcut triggered - taking screenshot")
            if self.screenshot_callback:
                self.screenshot_callback()
            else:
                print("⚠️  No screenshot callback configured")
        except Exception as e:
            print(f"Error in default keyboard callback: {e}")
