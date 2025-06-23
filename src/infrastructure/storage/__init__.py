"""
Storage infrastructure for ScreenAgent
Provides storage strategies and factory
"""

from .storage_strategy import IStorageStrategy, IStorageFactory
from .file_storage_strategy import FileStorageStrategy
from .memory_storage_strategy import MemoryStorageStrategy
from .storage_factory import StorageFactory, StorageManager

__all__ = [
    'IStorageStrategy',
    'IStorageFactory',
    'FileStorageStrategy',
    'MemoryStorageStrategy',
    'StorageFactory',
    'StorageManager'
]
