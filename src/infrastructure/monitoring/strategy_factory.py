"""
Factory for creating change detection strategies
"""
from typing import Dict, Type, Optional, Any
from ...domain.interfaces.change_detection_strategy import IChangeDetectionStrategy
from .threshold_detector import ThresholdDetector
from .pixel_diff_detector import PixelDiffDetector
from .hash_comparison_detector import HashComparisonDetector
from .change_detection_context import ChangeDetectionContext


class ChangeDetectionStrategyFactory:
    """Factory for creating and managing change detection strategies"""
    
    _strategies: Dict[str, Type[IChangeDetectionStrategy]] = {
        'threshold': ThresholdDetector,
        'pixel_diff': PixelDiffDetector,
        'hash_comparison': HashComparisonDetector
    }
    
    @classmethod
    def create_strategy(
        self, 
        strategy_type: str, 
        **kwargs
    ) -> Optional[IChangeDetectionStrategy]:
        """
        Create a change detection strategy
        
        Args:
            strategy_type: Type of strategy ('threshold', 'pixel_diff', 'hash_comparison')
            **kwargs: Additional arguments for strategy initialization
            
        Returns:
            Optional[IChangeDetectionStrategy]: Created strategy or None
        """
        if strategy_type not in self._strategies:
            return None
        
        try:
            strategy_class = self._strategies[strategy_type]
            strategy = strategy_class()
            
            # Apply any additional configuration
            if hasattr(strategy, 'configure') and kwargs:
                strategy.configure(**kwargs)
            
            return strategy
        except Exception:
            return None
    
    @classmethod
    def create_context_with_strategy(
        self, 
        strategy_type: str = 'threshold',
        **kwargs
    ) -> Optional[ChangeDetectionContext]:
        """
        Create a context with a default strategy
        
        Args:
            strategy_type: Default strategy type
            **kwargs: Strategy configuration
            
        Returns:
            Optional[ChangeDetectionContext]: Context with strategy or None
        """
        strategy = self.create_strategy(strategy_type, **kwargs)
        if not strategy:
            return None
        
        return ChangeDetectionContext(strategy)
    
    @classmethod
    def create_context_with_all_strategies(self) -> ChangeDetectionContext:
        """
        Create a context with all available strategies registered
        
        Returns:
            ChangeDetectionContext: Context with all strategies
        """
        # Start with threshold as default
        default_strategy = self.create_strategy('threshold')
        context = ChangeDetectionContext(default_strategy)
        
        # Register all other strategies
        for strategy_type in self._strategies.keys():
            if strategy_type != 'threshold':  # Skip threshold as it's already set
                strategy = self.create_strategy(strategy_type)
                if strategy:
                    context.register_strategy(strategy)
        
        return context
    
    @classmethod
    def get_available_strategy_types(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available strategy types
        
        Returns:
            Dict mapping strategy types to their descriptions
        """
        return {
            'threshold': {
                'name': 'Threshold Detector',
                'description': 'Simple size-based change detection',
                'speed': 'fast',
                'accuracy': 'basic',
                'memory_usage': 'low'
            },
            'pixel_diff': {
                'name': 'Pixel Difference Detector',
                'description': 'Pixel-by-pixel comparison analysis',
                'speed': 'slow',
                'accuracy': 'high',
                'memory_usage': 'high'
            },
            'hash_comparison': {
                'name': 'Hash Comparison Detector',
                'description': 'Hash-based exact change detection',
                'speed': 'fast',
                'accuracy': 'exact',
                'memory_usage': 'low'
            }
        }
    
    @classmethod
    def register_strategy(
        self, 
        strategy_type: str, 
        strategy_class: Type[IChangeDetectionStrategy]
    ) -> bool:
        """
        Register a new strategy type
        
        Args:
            strategy_type: Unique identifier for the strategy
            strategy_class: Strategy class implementing IChangeDetectionStrategy
            
        Returns:
            bool: True if registration successful
        """
        try:
            self._strategies[strategy_type] = strategy_class
            return True
        except Exception:
            return False
    
    @classmethod
    def get_recommended_strategy(
        self, 
        performance_priority: str = 'balanced'
    ) -> str:
        """
        Get recommended strategy based on performance priority
        
        Args:
            performance_priority: 'speed', 'accuracy', or 'balanced'
            
        Returns:
            str: Recommended strategy type
        """
        if performance_priority == 'speed':
            return 'threshold'
        elif performance_priority == 'accuracy':
            return 'pixel_diff'
        elif performance_priority == 'exact':
            return 'hash_comparison'
        else:  # balanced
            return 'threshold'  # Good balance of speed and usefulness
