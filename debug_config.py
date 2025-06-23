"""
Debug script to test the configuration repository directly
"""
import asyncio
import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from src.infrastructure.dependency_injection import setup_container, get_container
from src.domain.repositories.configuration_repository import IConfigurationRepository
from src.utils.platform_detection import is_wsl, is_windows, is_linux_with_display


async def test_config_repository():
    """Test the configuration repository directly"""
    try:
        # Setup DI container
        if is_wsl():
            platform_name = "wsl"
        elif is_windows():
            platform_name = "windows"
        elif is_linux_with_display():
            platform_name = "linux"
        else:
            platform_name = "unknown"
        
        config_dict = {
            "storage": {"type": "file", "base_path": "screenshots"},
            "monitoring": {"default_strategy": "threshold", "threshold": 20},
            "capture": {"platform": platform_name, "wsl_enabled": is_wsl()},
            "server": {"port": 8000, "max_port_attempts": 10},
            "config_file": "config/screen_agent_config.json"
        }
        
        setup_container(config_dict)
        container = get_container()
        
        # Get configuration repository
        config_repo = container.get(IConfigurationRepository)
        print(f"Got config repository: {type(config_repo)}")
        
        # Test get_all_config
        print("Testing get_all_config()...")
        all_config = await config_repo.get_all_config()
        print(f"All config result: {all_config}")
        
        # Test specific config
        print("Testing get_config('storage')...")
        storage_config = await config_repo.get_config('storage')
        print(f"Storage config: {storage_config}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_config_repository())
