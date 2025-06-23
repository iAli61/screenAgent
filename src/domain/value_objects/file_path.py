"""
File path value object
Immutable file path representation with validation
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os


@dataclass(frozen=True)
class FilePath:
    """Immutable file path value object"""
    
    path: str
    
    def __post_init__(self):
        """Validate file path"""
        if not self.path:
            raise ValueError("File path cannot be empty")
        
        # Handle Path objects
        if hasattr(self.path, 'absolute'):  # It's a Path object
            abs_path = str(self.path.absolute())
        else:
            # Convert to absolute path for consistency
            abs_path = os.path.abspath(str(self.path))
            
        object.__setattr__(self, 'path', abs_path)
    
    @property
    def name(self) -> str:
        """Get file name"""
        return Path(self.path).name
    
    @property
    def stem(self) -> str:
        """Get file name without extension"""
        return Path(self.path).stem
    
    @property
    def suffix(self) -> str:
        """Get file extension"""
        return Path(self.path).suffix
    
    @property
    def parent(self) -> 'DirectoryPath':
        """Get parent directory"""
        return DirectoryPath(str(Path(self.path).parent))
    
    @property
    def exists(self) -> bool:
        """Check if file exists"""
        return os.path.isfile(self.path)
        
    def unlink(self) -> bool:
        """Delete the file if it exists"""
        try:
            if self.exists:
                os.unlink(self.path)
                return True
            return False
        except Exception:
            return False
    
    @property
    def size_bytes(self) -> Optional[int]:
        """Get file size in bytes"""
        if self.exists:
            return os.path.getsize(self.path)
        return None
    
    def is_image(self) -> bool:
        """Check if file is an image"""
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
        return self.suffix.lower() in image_extensions
    
    def is_json(self) -> bool:
        """Check if file is JSON"""
        return self.suffix.lower() == '.json'
    
    def with_suffix(self, suffix: str) -> 'FilePath':
        """Create new file path with different suffix"""
        new_path = Path(self.path).with_suffix(suffix)
        return FilePath(str(new_path))
    
    def with_name(self, name: str) -> 'FilePath':
        """Create new file path with different name"""
        new_path = Path(self.path).with_name(name)
        return FilePath(str(new_path))
    
    def relative_to(self, base: 'DirectoryPath') -> str:
        """Get path relative to base directory"""
        try:
            return str(Path(self.path).relative_to(base.path))
        except ValueError:
            return self.path
    
    @classmethod
    def from_parts(cls, directory: str, filename: str) -> 'FilePath':
        """Create file path from directory and filename"""
        return cls(os.path.join(directory, filename))


@dataclass(frozen=True) 
class DirectoryPath:
    """Immutable directory path value object"""
    
    path: str
    
    def __post_init__(self):
        """Validate directory path"""
        if not self.path:
            raise ValueError("Directory path cannot be empty")
        
        # Convert to absolute path for consistency
        abs_path = os.path.abspath(self.path)
        object.__setattr__(self, 'path', abs_path)
    
    @property
    def name(self) -> str:
        """Get directory name"""
        return Path(self.path).name
    
    @property
    def parent(self) -> 'DirectoryPath':
        """Get parent directory"""
        return DirectoryPath(str(Path(self.path).parent))
    
    @property
    def exists(self) -> bool:
        """Check if directory exists"""
        return os.path.isdir(self.path)
    
    def create(self, exist_ok: bool = True) -> None:
        """Create directory if it doesn't exist"""
        os.makedirs(self.path, exist_ok=exist_ok)
    
    def join(self, *parts) -> 'DirectoryPath':
        """Join with additional path parts"""
        new_path = os.path.join(self.path, *parts)
        return DirectoryPath(new_path)
    
    def file(self, filename: str) -> FilePath:
        """Create file path within this directory"""
        return FilePath.from_parts(self.path, filename)
    
    def list_files(self, pattern: str = "*") -> list[FilePath]:
        """List files in directory matching pattern"""
        if not self.exists:
            return []
        
        files = []
        for file_path in Path(self.path).glob(pattern):
            if file_path.is_file():
                files.append(FilePath(str(file_path)))
        
        return files
    
    def list_subdirectories(self) -> list['DirectoryPath']:
        """List subdirectories"""
        if not self.exists:
            return []
        
        dirs = []
        for dir_path in Path(self.path).iterdir():
            if dir_path.is_dir():
                dirs.append(DirectoryPath(str(dir_path)))
        
        return dirs
