"""
Data Transfer Objects for the interfaces layer
"""

from .screenshot_dto import (
    ScreenshotRequest,
    ScreenshotResponse,
    ScreenshotListRequest,
    ScreenshotListResponse,
    ScreenshotDeleteRequest,
    ScreenshotDeleteResponse,
    ScreenshotInfoResponse
)

from .monitoring_dto import (
    MonitoringStartRequest,
    MonitoringStartResponse,
    MonitoringStopRequest,
    MonitoringStopResponse,
    MonitoringStatusResponse,
    MonitoringSessionListResponse,
    MonitoringSessionDetailsResponse
)

from .analysis_dto import (
    AnalysisRequest,
    AnalysisResponse,
    ComparisonRequest,
    ComparisonResponse,
    BatchAnalysisRequest,
    BatchAnalysisResponse,
    SimilaritySearchRequest,
    SimilaritySearchResponse,
    ThumbnailRequest,
    HistogramRequest,
    HistogramResponse
)

from .configuration_dto import (
    ConfigurationRequest,
    ConfigurationResponse,
    ConfigurationUpdateRequest,
    ConfigurationUpdateResponse,
    ConfigurationResetRequest,
    ConfigurationResetResponse,
    ConfigurationValidationRequest,
    ConfigurationValidationResponse,
    ConfigurationSchemaResponse
)

from .common_dto import (
    ErrorResponse,
    SuccessResponse,
    PaginationRequest,
    PaginationInfo,
    SortRequest,
    FilterRequest,
    HealthCheckResponse,
    FileUploadRequest,
    FileUploadResponse,
    BulkOperationRequest,
    BulkOperationResponse
)

__all__ = [
    # Screenshot DTOs
    'ScreenshotRequest',
    'ScreenshotResponse',
    'ScreenshotListRequest',
    'ScreenshotListResponse',
    'ScreenshotDeleteRequest',
    'ScreenshotDeleteResponse',
    'ScreenshotInfoResponse',
    
    # Monitoring DTOs
    'MonitoringStartRequest',
    'MonitoringStartResponse',
    'MonitoringStopRequest',
    'MonitoringStopResponse',
    'MonitoringStatusResponse',
    'MonitoringSessionListResponse',
    'MonitoringSessionDetailsResponse',
    
    # Analysis DTOs
    'AnalysisRequest',
    'AnalysisResponse',
    'ComparisonRequest',
    'ComparisonResponse',
    'BatchAnalysisRequest',
    'BatchAnalysisResponse',
    'SimilaritySearchRequest',
    'SimilaritySearchResponse',
    'ThumbnailRequest',
    'HistogramRequest',
    'HistogramResponse',
    
    # Configuration DTOs
    'ConfigurationRequest',
    'ConfigurationResponse',
    'ConfigurationUpdateRequest',
    'ConfigurationUpdateResponse',
    'ConfigurationResetRequest',
    'ConfigurationResetResponse',
    'ConfigurationValidationRequest',
    'ConfigurationValidationResponse',
    'ConfigurationSchemaResponse',
    
    # Common DTOs
    'ErrorResponse',
    'SuccessResponse',
    'PaginationRequest',
    'PaginationInfo',
    'SortRequest',
    'FilterRequest',
    'HealthCheckResponse',
    'FileUploadRequest',
    'FileUploadResponse',
    'BulkOperationRequest',
    'BulkOperationResponse'
]
