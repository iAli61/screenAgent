"""
Screenshot Service Implementation
Concrete implementation of screenshot capture and management
"""
import asyncio
import uuid
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import logging

from src.domain.interfaces.screenshot_service import IScreenshotService
from src.domain.interfaces.storage_service import IFileStorageService, IRepository
from src.domain.interfaces.event_service import IEventService
from src.domain.interfaces.capture_service import ICaptureService
from src.domain.entities.screenshot import Screenshot
from src.domain.entities.roi_region import ROIRegion
from src.domain.value_objects.coordinates import Rectangle
from src.domain.value_objects.timestamp import Timestamp
from src.domain.value_objects.file_path import FilePath
from src.domain.events.screenshot_captured import ScreenshotCaptured


logger = logging.getLogger(__name__)


class ScreenshotService(IScreenshotService):
    """Concrete implementation of screenshot service"""
    
    def __init__(
        self,
        file_storage: IFileStorageService,
        screenshot_repository: IRepository[Screenshot],
        event_service: IEventService,
        capture_service: ICaptureService
    ):
        self._file_storage = file_storage
        self._screenshot_repository = screenshot_repository
        self._event_service = event_service
        self._capture_service = capture_service
        
        # Generate a unique run ID when the service is initialized
        self._run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Create base directories for this run
        self._base_dir = Path(os.environ.get('SCREENSHOT_BASE_DIR', 
                                            str(Path.cwd() / 'screenshots')))
        self._run_dir = self._base_dir / self._run_id
        self._images_dir = self._run_dir / 'images'
        self._metadata_dir = self._run_dir / 'metadata'
        
        # Create directories
        self._images_dir.mkdir(parents=True, exist_ok=True)
        self._metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure repository to use run-specific directories if it's a FileScreenshotRepository
        if hasattr(self._screenshot_repository, 'metadata_directory'):
            self._screenshot_repository.metadata_directory = self._metadata_dir
            self._screenshot_repository.images_directory = self._images_dir
        
        logger.info(f"🚀 Screenshot service initialized with run ID: {self._run_id}")
        logger.info(f"📁 Images directory: {self._images_dir}")
        logger.info(f"📁 Metadata directory: {self._metadata_dir}")
        
    async def capture_full_screen(
        self, 
        monitor_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Screenshot:
        """Capture full screen screenshot"""
        try:
            # Use capture service to get screenshot data
            capture_result = await self._capture_service.capture_full_screen(monitor_id)
            
            if not capture_result.success:
                raise Exception(f"Capture failed: {capture_result.error}")
            
            # Create screenshot entity
            screenshot_id = str(uuid.uuid4())
            timestamp = Timestamp.now()
            file_path = FilePath(f"screenshot_{screenshot_id}.png")
            
            # Get dimensions from capture metadata or use defaults
            capture_metadata = capture_result.metadata or {}
            width = capture_metadata.get('width', 1920)
            height = capture_metadata.get('height', 1080)
            
            screenshot = Screenshot(
                id=screenshot_id,
                file_path=file_path,
                timestamp=timestamp,
                width=width,
                height=height,
                format="PNG",
                size_bytes=len(capture_result.data),
                metadata=metadata or {},
                data=capture_result.data  # Store binary data
            )
            
            # Save to repository
            await self._screenshot_repository.create(screenshot)
            
            # Save the actual image file
            await self.save_screenshot(screenshot)
            
            # Publish event
            event = ScreenshotCaptured(
                screenshot_id=screenshot_id,
                file_path=str(screenshot.file_path.path),
                capture_method="full_screen",
                monitor_id=monitor_id,
                width=screenshot.width,
                height=screenshot.height
            )
            await self._event_service.publish(event)
            
            logger.info(f"Captured full screen screenshot: {screenshot_id}")
            return screenshot
            
        except Exception as e:
            logger.error(f"Failed to capture full screen: {e}")
            raise
    
    async def capture_region(
        self, 
        region: Rectangle,
        monitor_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Screenshot:
        """Capture screenshot of specific region"""
        try:
            # Use capture service to get screenshot data
            capture_result = await self._capture_service.capture_region(region, monitor_id)
            
            if not capture_result.success:
                raise Exception(f"Region capture failed: {capture_result.error}")
            
            screenshot_id = str(uuid.uuid4())
            timestamp = Timestamp.now()
            file_path = FilePath(f"region_{screenshot_id}.png")
            
            # Create screenshot entity
            screenshot = Screenshot(
                id=screenshot_id,
                file_path=file_path,
                timestamp=timestamp,
                width=region.width,
                height=region.height,
                format="PNG",
                size_bytes=len(capture_result.data),
                metadata=metadata or {},
                data=capture_result.data
            )
            
            # Add region info to metadata
            screenshot.metadata.update({
                "region": {
                    "left": region.left,
                    "top": region.top,
                    "right": region.right,
                    "bottom": region.bottom,
                    "width": region.width,
                    "height": region.height
                }
            })
            
            await self._screenshot_repository.create(screenshot)
            
            # Save the actual image file
            await self.save_screenshot(screenshot)
            
            # Publish event
            event = ScreenshotCaptured(
                screenshot_id=screenshot_id,
                file_path=str(screenshot.file_path.path),
                capture_method="region",
                monitor_id=monitor_id,
                width=screenshot.width,
                height=screenshot.height
            )
            await self._event_service.publish(event)
            
            logger.info(f"Captured region screenshot: {screenshot_id}")
            return screenshot
            
        except Exception as e:
            logger.error(f"Failed to capture region: {e}")
            raise
    
    async def capture_roi(
        self, 
        roi: ROIRegion,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Screenshot:
        """Capture screenshot of ROI region"""
        try:
            # Convert ROI to rectangle and capture
            region = Rectangle(
                x=roi.coordinates.x,
                y=roi.coordinates.y,
                width=roi.coordinates.width,
                height=roi.coordinates.height
            )
            
            # Add ROI metadata
            roi_metadata = metadata or {}
            roi_metadata.update({
                "roi_id": roi.id,
                "roi_name": roi.name,
                "roi_tags": roi.tags
            })
            
            screenshot = await self.capture_region(region, metadata=roi_metadata)
            
            logger.info(f"Captured ROI screenshot: {roi.id}")
            return screenshot
            
        except Exception as e:
            logger.error(f"Failed to capture ROI {roi.id}: {e}")
            raise
    
    async def save_screenshot(
        self, 
        screenshot: Screenshot, 
        directory_path: Optional[Path] = None
    ) -> Path:
        """Save screenshot to storage"""
        try:
            if not screenshot.data:
                raise ValueError("Screenshot data is missing")
                
            # Use the run-specific images directory as the default
            if directory_path:
                save_path = directory_path
                save_path.mkdir(parents=True, exist_ok=True)
            else:
                save_path = self._images_dir
                
            # Extract filename from file_path or create a new one
            if hasattr(screenshot.file_path, 'path'):
                filename = Path(screenshot.file_path.path).name
            elif isinstance(screenshot.file_path, str):
                filename = Path(screenshot.file_path).name
            else:
                filename = f"screenshot_{screenshot.id}.png"
                
            # Save the file using storage service
            full_path = await self._file_storage.save_file(
                content=screenshot.data,
                filename=filename,
                directory=save_path,
                metadata=screenshot.metadata
            )
            
            # Update screenshot with saved path
            screenshot.file_path = FilePath(str(full_path))
            await self._screenshot_repository.update(screenshot)
            
            # Clear binary data from memory now that it's saved
            screenshot.data = None
            
            logger.info(f"💾 Screenshot saved: {full_path}")
            return full_path
            
        except Exception as e:
            logger.error(f"Failed to save screenshot {screenshot.id}: {e}")
            raise
    
    async def get_screenshot(self, screenshot_id: str) -> Optional[Screenshot]:
        """Retrieve screenshot by ID"""
        try:
            return await self._screenshot_repository.get_by_id(screenshot_id)
        except Exception as e:
            logger.error(f"Failed to get screenshot {screenshot_id}: {e}")
            return None
    
    async def list_screenshots(
        self, 
        session_id: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Screenshot]:
        """List screenshots with optional filtering"""
        try:
            if session_id:
                criteria = {"session_id": session_id}
                screenshots = await self._screenshot_repository.find_by_criteria(criteria)
            else:
                screenshots = await self._screenshot_repository.list_all(limit=limit, offset=offset)
            
            return screenshots
            
        except Exception as e:
            logger.error(f"Failed to list screenshots: {e}")
            return []
    
    async def delete_screenshot(self, screenshot_id: str) -> bool:
        """Delete screenshot by ID"""
        try:
            screenshot = await self._screenshot_repository.get_by_id(screenshot_id)
            if not screenshot:
                logger.warning(f"Screenshot not found for deletion: {screenshot_id}")
                return False
            
            # Delete file if it exists
            if screenshot.file_path:
                file_path = screenshot.file_path
                await self._file_storage.delete_file(file_path)
                logger.info(f"Deleted screenshot file: {file_path}")
            
            # Delete metadata file if it exists
            metadata_path = self._metadata_dir / f"{screenshot_id}.json"
            if metadata_path.exists():
                await self._file_storage.delete_file(metadata_path)
                logger.info(f"Deleted metadata file: {metadata_path}")
            
            # Delete from repository
            success = await self._screenshot_repository.delete(screenshot_id)
            
            if success:
                logger.info(f"Deleted screenshot: {screenshot_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete screenshot {screenshot_id}: {e}")
            return False
    
    async def cleanup_old_screenshots(
        self, 
        max_age_days: int = 30,
        max_count: Optional[int] = None
    ) -> int:
        """Clean up old screenshots based on age and count"""
        try:
            # TODO: Implement cleanup logic
            logger.info(f"Cleanup completed, would delete based on {max_age_days} days")
            return 0
            
        except Exception as e:
            logger.error(f"Failed to cleanup screenshots: {e}")
            return 0
