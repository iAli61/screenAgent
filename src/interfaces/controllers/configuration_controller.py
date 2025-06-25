"""
Configuration Controller
Handles configuration-related API endpoints
"""
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.domain.repositories.configuration_repository import IConfigurationRepository


class ConfigurationController:
    """Controller for configuration operations"""
    
    def __init__(self, configuration_repository: IConfigurationRepository):
        self.configuration_repository = configuration_repository
    
    async def get_configuration(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get current configuration"""
        try:
            config = await self.configuration_repository.get_all_config()
            
            return {
                'success': True,
                'configuration': {
                    'screenshot': config.get('screenshot', {}),
                    'monitoring': config.get('monitoring', {}),
                    'roi': config.get('roi', {}),
                    'llm': config.get('llm', {}),
                    'ui': config.get('ui', {}),
                    'server': config.get('server', {}),
                    'storage': config.get('storage', {})
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_configuration(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update configuration settings"""
        try:
            config_updates = request_data.get('configuration', {})
            
            if not config_updates:
                return {
                    'success': False,
                    'error': 'configuration data required'
                }
            
            # Validate configuration updates
            validation_result = self._validate_configuration(config_updates)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f"Invalid configuration: {validation_result['errors']}"
                }
            
            # Get current config
            current_config = await self.configuration_repository.get_all_config()
            
            # Merge updates
            updated_config = self._merge_config(current_config, config_updates)
            
            # Save updated configuration
            await self.configuration_repository.save_config(updated_config)
            
            return {
                'success': True,
                'message': 'Configuration updated successfully',
                'updated_fields': list(config_updates.keys()),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def reset_configuration(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Reset configuration to defaults"""
        try:
            section = request_data.get('section')
            
            # Get default configuration
            default_config = self._get_default_config()
            
            if section:
                # Reset specific section
                if section not in default_config:
                    return {
                        'success': False,
                        'error': f"Unknown configuration section: {section}"
                    }
                
                current_config = await self.configuration_repository.get_all_config()
                current_config[section] = default_config[section]
                await self.configuration_repository.save_config(current_config)
                
                return {
                    'success': True,
                    'message': f'Configuration section "{section}" reset to defaults',
                    'reset_section': section
                }
            else:
                # Reset entire configuration
                await self.configuration_repository.save_config(default_config)
                
                return {
                    'success': True,
                    'message': 'All configuration reset to defaults'
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_roi_config(self) -> Dict[str, Any]:
        """Get current ROI configuration"""
        try:
            roi = await self.configuration_repository.get_config("roi")
            
            return {
                'success': True,
                'roi': roi or [0, 0, 1920, 1080]  # Default ROI if none set
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def update_roi_config(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update ROI configuration"""
        try:
            roi_data = request_data.get('roi')
            
            if not roi_data or not isinstance(roi_data, list) or len(roi_data) != 4:
                return {
                    'success': False,
                    'error': 'ROI data must be an array of 4 numbers [x, y, width, height]'
                }
            
            x, y, width, height = roi_data
            
            # Validate ROI values
            if not all(isinstance(val, (int, float)) and val >= 0 for val in roi_data):
                return {
                    'success': False,
                    'error': 'ROI values must be non-negative numbers'
                }
            
            if width <= 0 or height <= 0:
                return {
                    'success': False,
                    'error': 'ROI width and height must be positive'
                }
            
            # Save ROI configuration
            success = await self.configuration_repository.set_config("roi", roi_data)
            
            if success:
                return {
                    'success': True,
                    'message': 'ROI configuration updated successfully',
                    'roi': roi_data,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to save ROI configuration'
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def validate_configuration(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration without saving"""
        try:
            config_to_validate = request_data.get('configuration', {})
            
            if not config_to_validate:
                return {
                    'success': False,
                    'error': 'configuration data required'
                }
            
            validation_result = self._validate_configuration(config_to_validate)
            
            return {
                'success': True,
                'validation': validation_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_configuration_schema(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get configuration schema"""
        try:
            schema = {
                'screenshot': {
                    'interval': {
                        'type': 'number',
                        'default': 5.0,
                        'min': 0.1,
                        'max': 3600.0,
                        'description': 'Screenshot interval in seconds'
                    },
                    'format': {
                        'type': 'string',
                        'default': 'PNG',
                        'enum': ['PNG', 'JPEG', 'BMP'],
                        'description': 'Screenshot image format'
                    },
                    'quality': {
                        'type': 'number',
                        'default': 95,
                        'min': 1,
                        'max': 100,
                        'description': 'JPEG quality (1-100)'
                    },
                    'auto_cleanup': {
                        'type': 'boolean',
                        'default': True,
                        'description': 'Automatically cleanup old screenshots'
                    },
                    'max_age_hours': {
                        'type': 'number',
                        'default': 24,
                        'min': 1,
                        'max': 8760,
                        'description': 'Maximum age of screenshots in hours'
                    }
                },
                'monitoring': {
                    'enabled': {
                        'type': 'boolean',
                        'default': True,
                        'description': 'Enable monitoring mode'
                    },
                    'change_threshold': {
                        'type': 'number',
                        'default': 20.0,
                        'min': 0.1,
                        'max': 100.0,
                        'description': 'Change detection threshold percentage'
                    },
                    'continuous_mode': {
                        'type': 'boolean',
                        'default': False,
                        'description': 'Run in continuous monitoring mode'
                    }
                },
                'roi': {
                    'enabled': {
                        'type': 'boolean',
                        'default': False,
                        'description': 'Enable ROI selection'
                    },
                    'x': {
                        'type': 'number',
                        'default': 0,
                        'min': 0,
                        'description': 'ROI X coordinate'
                    },
                    'y': {
                        'type': 'number',
                        'default': 0,
                        'min': 0,
                        'description': 'ROI Y coordinate'
                    },
                    'width': {
                        'type': 'number',
                        'default': 800,
                        'min': 1,
                        'description': 'ROI width'
                    },
                    'height': {
                        'type': 'number',
                        'default': 600,
                        'min': 1,
                        'description': 'ROI height'
                    }
                },
                'llm': {
                    'provider': {
                        'type': 'string',
                        'default': 'openai',
                        'enum': ['openai', 'anthropic', 'ollama', 'azure'],
                        'description': 'LLM provider'
                    },
                    'model': {
                        'type': 'string',
                        'default': 'gpt-4-vision-preview',
                        'description': 'Model name'
                    },
                    'api_key': {
                        'type': 'string',
                        'default': '',
                        'description': 'API key for the LLM provider'
                    },
                    'base_url': {
                        'type': 'string',
                        'default': '',
                        'description': 'Custom base URL for API requests'
                    },
                    'timeout': {
                        'type': 'number',
                        'default': 30,
                        'min': 1,
                        'max': 300,
                        'description': 'Request timeout in seconds'
                    }
                },
                'ui': {
                    'theme': {
                        'type': 'string',
                        'default': 'light',
                        'enum': ['light', 'dark', 'auto'],
                        'description': 'UI theme'
                    },
                    'auto_refresh': {
                        'type': 'boolean',
                        'default': True,
                        'description': 'Auto-refresh UI data'
                    },
                    'refresh_interval': {
                        'type': 'number',
                        'default': 5,
                        'min': 1,
                        'max': 60,
                        'description': 'UI refresh interval in seconds'
                    }
                },
                'server': {
                    'port': {
                        'type': 'number',
                        'default': 8000,
                        'min': 1024,
                        'max': 65535,
                        'description': 'Server port'
                    },
                    'host': {
                        'type': 'string',
                        'default': '127.0.0.1',
                        'description': 'Server host'
                    },
                    'cors_enabled': {
                        'type': 'boolean',
                        'default': True,
                        'description': 'Enable CORS'
                    }
                },
                'storage': {
                    'type': {
                        'type': 'string',
                        'default': 'file',
                        'enum': ['file', 'memory', 'database'],
                        'description': 'Storage backend type'
                    },
                    'base_path': {
                        'type': 'string',
                        'default': 'screenshots',
                        'description': 'Base path for file storage'
                    },
                    'max_storage_mb': {
                        'type': 'number',
                        'default': 1000,
                        'min': 100,
                        'max': 100000,
                        'description': 'Maximum storage size in MB'
                    }
                }
            }
            
            return {
                'success': True,
                'schema': schema
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration against schema"""
        errors = []
        schema = self._get_configuration_schema_dict()
        
        for section, settings in config.items():
            if section not in schema:
                errors.append(f"Unknown configuration section: {section}")
                continue
            
            section_schema = schema[section]
            
            for key, value in settings.items():
                if key not in section_schema:
                    errors.append(f"Unknown setting {section}.{key}")
                    continue
                
                field_schema = section_schema[key]
                field_type = field_schema.get('type')
                
                # Type validation
                if field_type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f"{section}.{key} must be a number")
                elif field_type == 'string' and not isinstance(value, str):
                    errors.append(f"{section}.{key} must be a string")
                elif field_type == 'boolean' and not isinstance(value, bool):
                    errors.append(f"{section}.{key} must be a boolean")
                
                # Range validation for numbers
                if field_type == 'number' and isinstance(value, (int, float)):
                    if 'min' in field_schema and value < field_schema['min']:
                        errors.append(f"{section}.{key} must be >= {field_schema['min']}")
                    if 'max' in field_schema and value > field_schema['max']:
                        errors.append(f"{section}.{key} must be <= {field_schema['max']}")
                
                # Enum validation
                if 'enum' in field_schema and value not in field_schema['enum']:
                    errors.append(f"{section}.{key} must be one of {field_schema['enum']}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _merge_config(self, current: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge configuration updates"""
        merged = current.copy()
        
        for key, value in updates.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_config(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'screenshot': {
                'interval': 5.0,
                'format': 'PNG',
                'quality': 95,
                'auto_cleanup': True,
                'max_age_hours': 24
            },
            'monitoring': {
                'enabled': True,
                'change_threshold': 20.0,
                'continuous_mode': False
            },
            'roi': {
                'enabled': False,
                'x': 0,
                'y': 0,
                'width': 800,
                'height': 600
            },
            'llm': {
                'provider': 'openai',
                'model': 'gpt-4-vision-preview',
                'api_key': '',
                'base_url': '',
                'timeout': 30
            },
            'ui': {
                'theme': 'light',
                'auto_refresh': True,
                'refresh_interval': 5
            },
            'server': {
                'port': 8000,
                'host': '127.0.0.1',
                'cors_enabled': True
            },
            'storage': {
                'type': 'file',
                'base_path': 'screenshots',
                'max_storage_mb': 1000
            }
        }
    
    def _get_configuration_schema_dict(self) -> Dict[str, Any]:
        """Get configuration schema as dictionary"""
        return {
            'screenshot': {
                'interval': {'type': 'number', 'min': 0.1, 'max': 3600.0},
                'format': {'type': 'string', 'enum': ['PNG', 'JPEG', 'BMP']},
                'quality': {'type': 'number', 'min': 1, 'max': 100},
                'auto_cleanup': {'type': 'boolean'},
                'max_age_hours': {'type': 'number', 'min': 1, 'max': 8760}
            },
            'monitoring': {
                'enabled': {'type': 'boolean'},
                'change_threshold': {'type': 'number', 'min': 0.1, 'max': 100.0},
                'continuous_mode': {'type': 'boolean'}
            },
            'roi': {
                'enabled': {'type': 'boolean'},
                'x': {'type': 'number', 'min': 0},
                'y': {'type': 'number', 'min': 0},
                'width': {'type': 'number', 'min': 1},
                'height': {'type': 'number', 'min': 1}
            },
            'llm': {
                'provider': {'type': 'string', 'enum': ['openai', 'anthropic', 'ollama', 'azure']},
                'model': {'type': 'string'},
                'api_key': {'type': 'string'},
                'base_url': {'type': 'string'},
                'timeout': {'type': 'number', 'min': 1, 'max': 300}
            },
            'ui': {
                'theme': {'type': 'string', 'enum': ['light', 'dark', 'auto']},
                'auto_refresh': {'type': 'boolean'},
                'refresh_interval': {'type': 'number', 'min': 1, 'max': 60}
            },
            'server': {
                'port': {'type': 'number', 'min': 1024, 'max': 65535},
                'host': {'type': 'string'},
                'cors_enabled': {'type': 'boolean'}
            },
            'storage': {
                'type': {'type': 'string', 'enum': ['file', 'memory', 'database']},
                'base_path': {'type': 'string'},
                'max_storage_mb': {'type': 'number', 'min': 100, 'max': 100000}
            }
        }
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health information"""
        try:
            # Get basic configuration status
            config = await self.configuration_repository.get_all_config()
            
            return {
                'success': True,
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'uptime': 'unknown',  # TODO: Track actual uptime
                'version': '1.0.0',   # TODO: Get from package info
                'environment': 'development',
                'components': {
                    'configuration': 'healthy',
                    'storage': 'healthy',
                    'api': 'healthy'
                },
                'metrics': {
                    'config_size': len(str(config)),
                    'last_updated': 'unknown'  # TODO: Track last update time
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'components': {
                    'configuration': 'error',
                    'storage': 'unknown',
                    'api': 'degraded'
                }
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Simple health check endpoint (synchronous)"""
        try:
            return {
                'status': 'ok',
                'timestamp': datetime.now().isoformat(),
                'checks': {
                    'controller': 'ok',
                    'repository': 'ok'  # TODO: Add actual repository health check
                },
                'response_time': 0.001  # TODO: Measure actual response time
            }
            
        except Exception as e:
            return {
                'status': 'error', 
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'checks': {
                    'controller': 'error',
                    'repository': 'unknown'
                }
            }
