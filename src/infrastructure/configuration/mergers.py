"""
Configuration mergers for ScreenAgent
Handles merging configuration from multiple sources with conflict resolution
"""
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import copy


class MergeStrategy(Enum):
    """Strategies for merging conflicting configuration values"""
    OVERRIDE = "override"           # Higher priority wins
    MERGE_OBJECTS = "merge_objects" # Merge dict/object values
    APPEND_LISTS = "append_lists"   # Append list values
    VALIDATE_FIRST = "validate_first" # Use first valid value


@dataclass
class MergeRule:
    """Rule for merging specific configuration keys"""
    key_pattern: str  # Regex pattern or exact key name
    strategy: MergeStrategy
    custom_merger: Optional[Callable[[Any, Any], Any]] = None
    description: str = ""


@dataclass
class MergeResult:
    """Result of a configuration merge operation"""
    merged_config: Dict[str, Any]
    conflicts: List[str]
    warnings: List[str]
    source_info: Dict[str, str]  # key -> source_name mapping


class ConfigurationMerger:
    """Merges configuration from multiple sources with conflict resolution"""
    
    def __init__(self):
        self._merge_rules: Dict[str, MergeRule] = {}
        self._default_strategy = MergeStrategy.OVERRIDE
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default merge rules for common configuration keys"""
        rules = [
            MergeRule(
                key_pattern="roi",
                strategy=MergeStrategy.VALIDATE_FIRST,
                description="Use first valid ROI coordinates"
            ),
            MergeRule(
                key_pattern="keyboard_shortcuts",
                strategy=MergeStrategy.MERGE_OBJECTS,
                description="Merge keyboard shortcut mappings"
            ),
            MergeRule(
                key_pattern=".*_list$",
                strategy=MergeStrategy.APPEND_LISTS,
                description="Append list values for keys ending in '_list'"
            ),
            MergeRule(
                key_pattern=".*_mapping$",
                strategy=MergeStrategy.MERGE_OBJECTS,
                description="Merge object values for keys ending in '_mapping'"
            ),
            MergeRule(
                key_pattern="api_keys",
                strategy=MergeStrategy.MERGE_OBJECTS,
                description="Merge API key configurations"
            )
        ]
        
        for rule in rules:
            self._merge_rules[rule.key_pattern] = rule
    
    def merge_configurations(
        self,
        configs: List[Dict[str, Any]],
        source_names: Optional[List[str]] = None
    ) -> MergeResult:
        """
        Merge multiple configurations with conflict resolution
        
        Args:
            configs: List of configuration dictionaries (highest priority first)
            source_names: Optional list of source names for debugging
            
        Returns:
            MergeResult with merged configuration and metadata
        """
        if not configs:
            return MergeResult({}, [], [], {})
        
        if source_names is None:
            source_names = [f"source_{i}" for i in range(len(configs))]
        
        merged = {}
        conflicts = []
        warnings = []
        source_info = {}
        
        # Collect all keys from all configs
        all_keys = set()
        for config in configs:
            all_keys.update(config.keys())
        
        # Merge each key
        for key in all_keys:
            values = []
            sources = []
            
            # Collect values from all configs that have this key
            for i, config in enumerate(configs):
                if key in config:
                    values.append(config[key])
                    sources.append(source_names[i])
            
            # Apply merge strategy
            if len(values) == 1:
                # No conflict - single value
                merged[key] = values[0]
                source_info[key] = sources[0]
            else:
                # Multiple values - apply merge strategy
                merge_result = self._merge_key_values(key, values, sources)
                merged[key] = merge_result["value"]
                source_info[key] = merge_result["source"]
                
                if merge_result["conflict"]:
                    conflicts.append(f"{key}: {merge_result['conflict']}")
                
                if merge_result["warning"]:
                    warnings.append(f"{key}: {merge_result['warning']}")
        
        return MergeResult(merged, conflicts, warnings, source_info)
    
    def _merge_key_values(
        self,
        key: str,
        values: List[Any],
        sources: List[str]
    ) -> Dict[str, Any]:
        """
        Merge values for a specific key using appropriate strategy
        
        Returns:
            Dict with "value", "source", "conflict", "warning" keys
        """
        if not values:
            return {"value": None, "source": "", "conflict": "", "warning": ""}
        
        # Find applicable merge rule
        merge_rule = self._find_merge_rule(key)
        strategy = merge_rule.strategy if merge_rule else self._default_strategy
        
        try:
            if merge_rule and merge_rule.custom_merger:
                # Use custom merger function
                merged_value = merge_rule.custom_merger(values[0], values[1:])
                return {
                    "value": merged_value,
                    "source": f"custom_merge({','.join(sources)})",
                    "conflict": "",
                    "warning": ""
                }
            
            elif strategy == MergeStrategy.OVERRIDE:
                # Highest priority wins
                return {
                    "value": values[0],
                    "source": sources[0],
                    "conflict": f"Multiple values, using {sources[0]}",
                    "warning": ""
                }
            
            elif strategy == MergeStrategy.MERGE_OBJECTS:
                # Merge dictionary/object values
                if all(isinstance(v, dict) for v in values):
                    merged_dict = {}
                    for value in reversed(values):  # Start with lowest priority
                        merged_dict.update(value)
                    return {
                        "value": merged_dict,
                        "source": f"merged({','.join(sources)})",
                        "conflict": "",
                        "warning": ""
                    }
                else:
                    return {
                        "value": values[0],
                        "source": sources[0],
                        "conflict": "",
                        "warning": f"Cannot merge non-dict values, using {sources[0]}"
                    }
            
            elif strategy == MergeStrategy.APPEND_LISTS:
                # Append list values
                if all(isinstance(v, list) for v in values):
                    merged_list = []
                    for value in reversed(values):  # Start with lowest priority
                        merged_list.extend(value)
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_list = []
                    for item in merged_list:
                        if item not in seen:
                            unique_list.append(item)
                            seen.add(item)
                    return {
                        "value": unique_list,
                        "source": f"appended({','.join(sources)})",
                        "conflict": "",
                        "warning": ""
                    }
                else:
                    return {
                        "value": values[0],
                        "source": sources[0],
                        "conflict": "",
                        "warning": f"Cannot append non-list values, using {sources[0]}"
                    }
            
            elif strategy == MergeStrategy.VALIDATE_FIRST:
                # Use first valid value (requires validation)
                from .validators import ConfigurationValidator
                validator = ConfigurationValidator()
                
                for i, value in enumerate(values):
                    is_valid, _ = validator.validate_value(key, value)
                    if is_valid:
                        return {
                            "value": value,
                            "source": sources[i],
                            "conflict": f"Multiple values, using first valid from {sources[i]}",
                            "warning": ""
                        }
                
                # No valid values found, use first
                return {
                    "value": values[0],
                    "source": sources[0],
                    "conflict": "",
                    "warning": f"No valid values found, using {sources[0]} anyway"
                }
            
            else:
                # Fallback to override
                return {
                    "value": values[0],
                    "source": sources[0],
                    "conflict": f"Unknown merge strategy, using {sources[0]}",
                    "warning": ""
                }
                
        except Exception as e:
            return {
                "value": values[0],
                "source": sources[0],
                "conflict": "",
                "warning": f"Merge error: {str(e)}, using {sources[0]}"
            }
    
    def _find_merge_rule(self, key: str) -> Optional[MergeRule]:
        """Find the applicable merge rule for a configuration key"""
        import re
        
        for pattern, rule in self._merge_rules.items():
            try:
                if re.match(pattern, key):
                    return rule
            except re.error:
                # If pattern is invalid regex, try exact match
                if pattern == key:
                    return rule
        
        return None
    
    def add_merge_rule(self, rule: MergeRule):
        """Add a custom merge rule"""
        self._merge_rules[rule.key_pattern] = rule
    
    def remove_merge_rule(self, key_pattern: str):
        """Remove a merge rule"""
        if key_pattern in self._merge_rules:
            del self._merge_rules[key_pattern]
    
    def set_default_strategy(self, strategy: MergeStrategy):
        """Set the default merge strategy"""
        self._default_strategy = strategy
    
    def get_merge_rules(self) -> Dict[str, MergeRule]:
        """Get all merge rules"""
        return self._merge_rules.copy()


class SmartConfigurationMerger(ConfigurationMerger):
    """Enhanced merger with intelligent conflict resolution"""
    
    def __init__(self):
        super().__init__()
        self._add_smart_rules()
    
    def _add_smart_rules(self):
        """Add intelligent merge rules for common scenarios"""
        
        # Custom merger for API configurations
        def merge_api_configs(primary: Dict, others: List[Dict]) -> Dict:
            """Smart merge for API configurations"""
            merged = copy.deepcopy(primary)
            
            for other in others:
                for key, value in other.items():
                    if key not in merged or not merged[key]:
                        # Use value if primary doesn't have it or it's empty
                        merged[key] = value
                    elif key.endswith('_key') or key.endswith('_token'):
                        # For API keys, prefer non-empty values
                        if value and (not merged[key] or len(str(value)) > len(str(merged[key]))):
                            merged[key] = value
            
            return merged
        
        # Custom merger for path configurations
        def merge_paths(primary: str, others: List[str]) -> str:
            """Smart merge for file/directory paths"""
            import os
            
            # Prefer absolute paths over relative
            all_paths = [primary] + others
            absolute_paths = [p for p in all_paths if os.path.isabs(p)]
            
            if absolute_paths:
                return absolute_paths[0]
            else:
                return primary
        
        # Custom merger for numeric ranges
        def merge_numeric_ranges(primary: Union[int, float], others: List[Union[int, float]]) -> Union[int, float]:
            """Smart merge for numeric values - use most reasonable value"""
            all_values = [primary] + others
            
            # Remove outliers and use median
            all_values.sort()
            median_idx = len(all_values) // 2
            return all_values[median_idx]
        
        # Add smart rules
        smart_rules = [
            MergeRule(
                key_pattern=".*api.*",
                strategy=MergeStrategy.OVERRIDE,
                custom_merger=lambda p, o: merge_api_configs(p, o),
                description="Smart merge for API configurations"
            ),
            MergeRule(
                key_pattern=".*_path$|.*_dir$",
                strategy=MergeStrategy.OVERRIDE,
                custom_merger=lambda p, o: merge_paths(p, o),
                description="Smart merge for file/directory paths"
            ),
            MergeRule(
                key_pattern=".*threshold$|.*interval$|.*timeout$",
                strategy=MergeStrategy.OVERRIDE,
                custom_merger=lambda p, o: merge_numeric_ranges(p, o),
                description="Smart merge for numeric ranges"
            )
        ]
        
        for rule in smart_rules:
            self.add_merge_rule(rule)
