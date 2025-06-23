"""
Common Data Transfer Objects
Used across multiple controllers
"""
from dataclasses import dataclass
from typing import Optional, Any, Dict, List


@dataclass
class ErrorResponse:
    """Standard error response"""
    success: bool = False
    error: str = ""
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@dataclass
class SuccessResponse:
    """Standard success response"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


@dataclass
class PaginationRequest:
    """Standard pagination request"""
    limit: Optional[int] = None
    offset: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


@dataclass
class PaginationInfo:
    """Pagination information"""
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool


@dataclass
class SortRequest:
    """Standard sorting request"""
    sort_by: Optional[str] = None
    sort_order: Optional[str] = None  # 'asc' or 'desc'


@dataclass
class FilterRequest:
    """Standard filtering request"""
    filters: Optional[Dict[str, Any]] = None
    search: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass
class HealthCheckResponse:
    """Health check response"""
    success: bool
    status: str
    timestamp: str
    version: Optional[str] = None
    uptime_seconds: Optional[float] = None
    components: Optional[Dict[str, str]] = None


@dataclass
class FileUploadRequest:
    """File upload request"""
    file_data: bytes
    filename: str
    content_type: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FileUploadResponse:
    """File upload response"""
    success: bool
    file_id: Optional[str] = None
    filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    error: Optional[str] = None


@dataclass
class BulkOperationRequest:
    """Bulk operation request"""
    operation: str
    items: List[Any]
    options: Optional[Dict[str, Any]] = None


@dataclass
class BulkOperationResponse:
    """Bulk operation response"""
    success: bool
    operation: str
    total_items: int
    successful_items: int
    failed_items: int
    results: List[Dict[str, Any]]
    errors: List[str]
