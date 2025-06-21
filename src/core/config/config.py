"""
Configuration management for ScreenAgent
"""
import os
import json
from typing import Any, Optional, Dict, Tuple

# Load environment variables if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional
    pass


class Config:
    """Configuration manager for ScreenAgent"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'screen_agent_config.json'
        )
        self._config_cache = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    self._config_cache = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
                self._config_cache = {}
        else:
            self._config_cache = {}
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self._config_cache, f, indent=2)
            return True
        except (IOError, OSError) as e:
            print(f"Error saving config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config_cache.get(key, self._get_default(key, default))
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        self._config_cache[key] = value
        return self._save_config()
    
    def _get_default(self, key: str, fallback: Any = None) -> Any:
        """Get default values for configuration keys"""
        defaults = {
            'roi': (100, 100, 800, 800),
            'port': 8000,
            'max_port_attempts': 10,
            'change_threshold': 20,
            'check_interval': 0.5,
            'llm_enabled': os.getenv('LLM_ENABLED', 'false').lower() == 'true',
            'llm_model': os.getenv('LLM_MODEL', 'gpt-4o'),
            'llm_prompt': os.getenv('LLM_PROMPT', 'Describe what you see in this screenshot, focusing on the most important elements.'),
            'temp_screenshot_path': os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                'temp',
                'temp_screenshot.png'
            ),
            'keyboard_shortcut': 'f12',
            'max_screenshots': 100,  # Maximum number of screenshots to keep
            'auto_cleanup': True,   # Automatically remove old screenshots
            # Storage configuration
            'storage_type': 'filesystem',  # Default to file-based storage for persistence
            'screenshot_dir': os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
                'screenshots'
            ),
        }
        
        return defaults.get(key, fallback)
    
    @property
    def roi(self) -> Tuple[int, int, int, int]:
        """Get current ROI as tuple (left, top, right, bottom)"""
        roi = self.get('roi')
        if isinstance(roi, (list, tuple)) and len(roi) == 4:
            return tuple(map(int, roi))
        return (100, 100, 800, 800)
    
    @roi.setter
    def roi(self, value: Tuple[int, int, int, int]):
        """Set ROI"""
        if len(value) == 4:
            self.set('roi', list(value))
    
    @property
    def port(self) -> int:
        """Get server port"""
        return int(self.get('port', 8000))
    
    @property
    def max_port_attempts(self) -> int:
        """Get maximum port attempts"""
        return int(self.get('max_port_attempts', 10))
    
    @property
    def change_threshold(self) -> float:
        """Get change detection threshold"""
        return float(self.get('change_threshold', 20))
    
    @change_threshold.setter
    def change_threshold(self, value: float):
        """Set change detection threshold"""
        self.set('change_threshold', float(value))
    
    @property
    def check_interval(self) -> float:
        """Get check interval in seconds"""
        return float(self.get('check_interval', 0.5))
    
    @check_interval.setter
    def check_interval(self, value: float):
        """Set check interval"""
        self.set('check_interval', float(value))
    
    @property
    def llm_enabled(self) -> bool:
        """Check if LLM is enabled"""
        return bool(self.get('llm_enabled', False))
    
    @llm_enabled.setter
    def llm_enabled(self, value: bool):
        """Set LLM enabled status"""
        self.set('llm_enabled', bool(value))
    
    @property
    def llm_model(self) -> str:
        """Get LLM model"""
        return str(self.get('llm_model', 'gpt-4o'))
    
    @llm_model.setter
    def llm_model(self, value: str):
        """Set LLM model"""
        self.set('llm_model', str(value))
    
    @property
    def llm_prompt(self) -> str:
        """Get LLM prompt"""
        return str(self.get('llm_prompt', 'Describe what you see in this screenshot.'))
    
    @llm_prompt.setter
    def llm_prompt(self, value: str):
        """Set LLM prompt"""
        self.set('llm_prompt', str(value))
    
    @property
    def temp_screenshot_path(self) -> str:
        """Get temporary screenshot path"""
        return str(self.get('temp_screenshot_path'))
    
    @property
    def storage_type(self) -> str:
        """Get storage type"""
        return str(self.get('storage_type', 'filesystem'))
    
    @property
    def screenshot_dir(self) -> str:
        """Get screenshot directory"""
        return str(self.get('screenshot_dir'))

    def to_dict(self) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return self._config_cache.copy()
    
    def update(self, data: Dict[str, Any]) -> bool:
        """Update multiple configuration values"""
        self._config_cache.update(data)
        return self._save_config()
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        self._config_cache = {}
        return self._save_config()
