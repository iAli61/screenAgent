"""
Analysis-related Data Transfer Objects
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class AnalysisRequest:
    """Request for screenshot analysis"""
    screenshot_id: str
    analysis_type: Optional[str] = None
    prompt: Optional[str] = None
    compare_with: Optional[str] = None


@dataclass
class AnalysisResponse:
    """Response containing analysis results"""
    success: bool
    analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class ComparisonRequest:
    """Request to compare two screenshots"""
    screenshot1_id: str
    screenshot2_id: str
    threshold: Optional[float] = None


@dataclass
class ComparisonResponse:
    """Response containing comparison results"""
    success: bool
    comparison: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class BatchAnalysisRequest:
    """Request for batch analysis"""
    screenshot_ids: List[str]
    analysis_types: Optional[List[str]] = None


@dataclass
class BatchAnalysisResponse:
    """Response containing batch analysis results"""
    success: bool
    batch_analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class SimilaritySearchRequest:
    """Request to find similar screenshots"""
    reference_id: str
    similarity_threshold: Optional[float] = None
    limit: Optional[int] = None


@dataclass
class SimilaritySearchResponse:
    """Response containing similar screenshots"""
    success: bool
    similar_screenshots: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class ThumbnailRequest:
    """Request to generate thumbnail"""
    screenshot_id: str
    size: Optional[List[int]] = None


@dataclass
class HistogramRequest:
    """Request to get color histogram"""
    screenshot_id: str


@dataclass
class HistogramResponse:
    """Response containing histogram data"""
    success: bool
    histogram: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
