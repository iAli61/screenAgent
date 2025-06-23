"""
Analysis Service Interface
Defines the contract for screenshot analysis and comparison
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from ..entities.screenshot import Screenshot
from ..entities.analysis_result import AnalysisResult
from ..entities.roi_region import ROIRegion


class IAnalysisService(ABC):
    """Interface for screenshot analysis services"""
    
    @abstractmethod
    async def compare_screenshots(
        self, 
        screenshot1: Screenshot, 
        screenshot2: Screenshot,
        region: Optional[ROIRegion] = None
    ) -> AnalysisResult:
        """
        Compare two screenshots and return analysis result
        
        Args:
            screenshot1: First screenshot to compare
            screenshot2: Second screenshot to compare
            region: Optional ROI region to focus comparison
            
        Returns:
            AnalysisResult with comparison metrics
        """
        pass
    
    @abstractmethod
    async def detect_changes(
        self, 
        reference_screenshot: Screenshot,
        current_screenshot: Screenshot,
        threshold: float = 20.0,
        region: Optional[ROIRegion] = None
    ) -> Tuple[bool, float]:
        """
        Detect if changes occurred between screenshots
        
        Args:
            reference_screenshot: Reference screenshot
            current_screenshot: Current screenshot to compare
            threshold: Change detection threshold (0-100)
            region: Optional ROI region to focus detection
            
        Returns:
            Tuple of (changes_detected, change_score)
        """
        pass
    
    @abstractmethod
    async def extract_text(self, screenshot: Screenshot) -> List[str]:
        """
        Extract text from screenshot using OCR
        
        Args:
            screenshot: Screenshot to analyze
            
        Returns:
            List of extracted text strings
        """
        pass
    
    @abstractmethod
    async def detect_objects(
        self, 
        screenshot: Screenshot
    ) -> List[Dict[str, Any]]:
        """
        Detect objects in screenshot
        
        Args:
            screenshot: Screenshot to analyze
            
        Returns:
            List of detected objects with coordinates and confidence
        """
        pass
    
    @abstractmethod
    async def analyze_image_quality(self, screenshot: Screenshot) -> Dict[str, Any]:
        """
        Analyze image quality metrics
        
        Args:
            screenshot: Screenshot to analyze
            
        Returns:
            Dictionary with quality metrics (blur, noise, brightness, etc.)
        """
        pass
    
    @abstractmethod
    async def generate_thumbnail(
        self, 
        screenshot: Screenshot, 
        size: Tuple[int, int] = (200, 150)
    ) -> bytes:
        """
        Generate thumbnail image
        
        Args:
            screenshot: Screenshot to create thumbnail from
            size: Thumbnail dimensions (width, height)
            
        Returns:
            Thumbnail image as bytes
        """
        pass
    
    @abstractmethod
    async def calculate_histogram(self, screenshot: Screenshot) -> Dict[str, List[int]]:
        """
        Calculate color histogram for screenshot
        
        Args:
            screenshot: Screenshot to analyze
            
        Returns:
            Dictionary with RGB histogram data
        """
        pass
    
    @abstractmethod
    async def find_similar_screenshots(
        self, 
        reference_screenshot: Screenshot,
        candidate_screenshots: List[Screenshot],
        similarity_threshold: float = 0.8
    ) -> List[Tuple[Screenshot, float]]:
        """
        Find similar screenshots from candidates
        
        Args:
            reference_screenshot: Reference screenshot
            candidate_screenshots: List of screenshots to compare
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of tuples (screenshot, similarity_score) sorted by similarity
        """
        pass
    
    @abstractmethod
    async def batch_analyze(
        self, 
        screenshots: List[Screenshot],
        analysis_types: List[str]
    ) -> List[AnalysisResult]:
        """
        Perform batch analysis on multiple screenshots
        
        Args:
            screenshots: List of screenshots to analyze
            analysis_types: Types of analysis to perform
            
        Returns:
            List of analysis results
        """
        pass
