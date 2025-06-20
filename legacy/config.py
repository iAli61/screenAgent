import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration file path
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screen_agent_config.json')

# Default configuration values
DEFAULT_ROI = (100, 100, 800, 800)  # (left, top, right, bottom)
DEFAULT_PORT = 8000
MAX_PORT_ATTEMPTS = 10  # Try up to 10 ports if the initial one is in use
CHANGE_THRESHOLD = 20  # Pixel difference threshold to trigger screenshot
CHECK_INTERVAL = 0.5  # Seconds between checks for ROI changes
TEMP_SCREENSHOT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp_screenshot.png')

# LLM configuration defaults
DEFAULT_LLM_ENABLED = os.getenv('LLM_ENABLED', 'false').lower() == 'true'
DEFAULT_LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-4o')
DEFAULT_LLM_PROMPT = os.getenv('LLM_PROMPT', 'Describe what you see in this screenshot, focusing on the most important elements.')

def save_to_config(key, value):
    """Save a key-value pair to the configuration file"""
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            pass
    config[key] = value
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
        print(f"{key} saved to {CONFIG_FILE}")
        return True
    except Exception as e:
        print(f"Error saving {key}: {e}")
        return False

def load_from_config(key, default=None):
    """Load a value from the configuration file by key"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                return config.get(key, default)
        except Exception as e:
            print(f"Error loading {key}: {e}")
    return default