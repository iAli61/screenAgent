"""
Screenshot-related Data Transfer Objects
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class ScreenshotRequest:
    """Request to capture a screenshot"""
    roi_enabled: Optional[bool] = None
    roi_x: Optional[int] = None
    roi_y: Optional[int] = None
    roi_width: Optional[int] = None
    roi_height: Optional[int] = None
    format: Optional[str] = None
    quality: Optional[int] = None
    filename: Optional[str] = None


@dataclass
class ScreenshotResponse:
    """Response containing screenshot information"""
    success: bool
    screenshot_id: Optional[str] = None
    filename: Optional[str] = None
    file_path: Optional[str] = None
    timestamp: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    format: Optional[str] = None
    file_size: Optional[int] = None
    error: Optional[str] = None


@dataclass
class ScreenshotListRequest:
    """Request to list screenshots"""
    limit: Optional[int] = None
    offset: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    format_filter: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None


@dataclass
class ScreenshotListResponse:
    """Response containing list of screenshots"""
    success: bool
    screenshots: List[Dict[str, Any]]
    total_count: int
    page_info: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class ScreenshotDeleteRequest:
    """Request to delete screenshot(s)"""
    screenshot_id: Optional[str] = None
    screenshot_ids: Optional[List[str]] = None
    older_than_hours: Optional[int] = None
    delete_all: Optional[bool] = None


@dataclass
class ScreenshotDeleteResponse:
    """Response after deleting screenshot(s)"""
    success: bool
    deleted_count: int
    deleted_ids: List[str]
    freed_space_mb: Optional[float] = None
    error: Optional[str] = None


@dataclass
class ScreenshotInfoResponse:
    """Detailed screenshot information response"""
    success: bool
    screenshot: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
