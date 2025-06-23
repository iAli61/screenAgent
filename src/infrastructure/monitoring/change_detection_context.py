"""
Change detection context for managing detection strategies
"""
from typing import Dict, Any, Optional
from ...domain.interfaces.change_detection_strategy import (
    IChangeDetectionStrategy, 
    IChangeDetectionContext
)


class ChangeDetectionContext(IChangeDetectionContext):
    """
    Context class for managing and switching between change detection strategies
    """
    
    def __init__(self, default_strategy: Optional[IChangeDetectionStrategy] = None):
        self._current_strategy: Optional[IChangeDetectionStrategy] = default_strategy
        self._strategies: Dict[str, IChangeDetectionStrategy] = {}
        
        if default_strategy:
            self._strategies[default_strategy.get_strategy_name()] = default_strategy
    
    def set_strategy(self, strategy: IChangeDetectionStrategy) -> bool:
        """Set the active change detection strategy"""
        try:
            if not strategy:
                return False
            
            self._current_strategy = strategy
            strategy_name = strategy.get_strategy_name()
            self._strategies[strategy_name] = strategy
            
            return True
        except Exception:
            return False
    
    def get_current_strategy(self) -> Optional[IChangeDetectionStrategy]:
        """Get the currently active strategy"""
        return self._current_strategy
    
    def detect_changes(
        self, 
        current_image: bytes, 
        threshold: float = 20.0
    ) -> Dict[str, Any]:
        """Detect changes using the current strategy"""
        if not self._current_strategy:
            return {
                'has_changes': False,
                'change_score': 0.0,
                'error': 'No strategy set',
                'metadata': {}
            }
        
        try:
            result = self._current_strategy.detect_changes(current_image, threshold)
            
            # Add context metadata
            if 'metadata' not in result:
                result['metadata'] = {}
            
            result['metadata']['strategy_name'] = self._current_strategy.get_strategy_name()
            result['metadata']['context_info'] = {
                'available_strategies': list(self._strategies.keys()),
                'active_strategy': self._current_strategy.get_strategy_name()
            }
            
            return result
        except Exception as e:
            return {
                'has_changes': False,
                'change_score': 0.0,
                'error': f'Strategy execution failed: {str(e)}',
                'metadata': {}
            }
    
    def initialize_baseline(self, baseline_image: bytes) -> bool:
        """Initialize baseline for current strategy"""
        if not self._current_strategy:
            return False
        
        return self._current_strategy.initialize(baseline_image)
    
    def update_baseline(self, new_baseline: bytes) -> bool:
        """Update baseline for current strategy"""
        if not self._current_strategy:
            return False
        
        return self._current_strategy.update_baseline(new_baseline)
    
    def register_strategy(self, strategy: IChangeDetectionStrategy) -> bool:
        """
        Register a strategy without making it active
        
        Args:
            strategy: Strategy to register
            
        Returns:
            bool: True if registration successful
        """
        try:
            strategy_name = strategy.get_strategy_name()
            self._strategies[strategy_name] = strategy
            return True
        except Exception:
            return False
    
    def switch_to_strategy(self, strategy_name: str) -> bool:
        """
        Switch to a previously registered strategy
        
        Args:
            strategy_name: Name of strategy to switch to
            
        Returns:
            bool: True if switch successful
        """
        if strategy_name in self._strategies:
            self._current_strategy = self._strategies[strategy_name]
            return True
        return False
    
    def get_available_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all available strategies
        
        Returns:
            Dict mapping strategy names to their metadata
        """
        return {
            name: strategy.get_strategy_metadata()
            for name, strategy in self._strategies.items()
        }
    
    def reset_current_strategy(self) -> bool:
        """Reset the current strategy"""
        if not self._current_strategy:
            return False
        
        return self._current_strategy.reset()
    
    def reset_all_strategies(self) -> bool:
        """Reset all registered strategies"""
        try:
            for strategy in self._strategies.values():
                strategy.reset()
            return True
        except Exception:
            return False
    
    def get_context_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of the detection context
        
        Returns:
            Dict with context status information
        """
        current_name = None
        current_metadata = None
        
        if self._current_strategy:
            current_name = self._current_strategy.get_strategy_name()
            current_metadata = self._current_strategy.get_strategy_metadata()
        
        return {
            'current_strategy': current_name,
            'current_strategy_metadata': current_metadata,
            'available_strategies': list(self._strategies.keys()),
            'total_strategies': len(self._strategies),
            'all_strategies_metadata': self.get_available_strategies()
        }
