"""
Models API Blueprint
Handles LLM provider and model information endpoints
"""
from flask_restx import Namespace, Resource, fields
from src.api.llm_api import LLMAnalyzer
from src.infrastructure.dependency_injection.container import get_container

# Create namespace for models
models_bp = Namespace('models', description='LLM provider and model information')

# API Models for documentation
provider_model = models_bp.model('Provider', {
    'name': fields.String(required=True, description='Provider name'),
    'models': fields.List(fields.String, description='Available models for this provider')
})

models_response_model = models_bp.model('ModelsResponse', {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'providers': fields.List(fields.Nested(provider_model), description='List of available providers'),
    'total_providers': fields.Integer(description='Total number of providers'),
    'total_models': fields.Integer(description='Total number of models across all providers')
})

provider_info_model = models_bp.model('ProviderInfo', {
    'success': fields.Boolean(required=True, description='Operation success status'),
    'provider': fields.String(description='Provider name'),
    'models': fields.List(fields.String, description='Available models'),
    'available': fields.Boolean(description='Whether provider is available')
})


@models_bp.route('')
class ModelsList(Resource):
    @models_bp.marshal_with(models_response_model)
    @models_bp.doc('get_models')
    def get(self):
        """Get all available LLM providers and their models"""
        try:
            # Create a temporary LLM analyzer to get provider/model info
            analyzer = LLMAnalyzer({'llm_enabled': True})
            
            available_providers = analyzer.get_available_providers()
            all_models = analyzer.get_available_models()
            
            providers = []
            total_models = 0
            
            for provider_name in available_providers:
                models_list = all_models.get(provider_name, [])
                providers.append({
                    'name': provider_name,
                    'models': models_list
                })
                total_models += len(models_list)
            
            return {
                'success': True,
                'providers': providers,
                'total_providers': len(providers),
                'total_models': total_models
            }
            
        except Exception as e:
            return {
                'success': False,
                'providers': [],
                'total_providers': 0,
                'total_models': 0,
                'error': str(e)
            }


@models_bp.route('/<string:provider>')
class ProviderInfo(Resource):
    @models_bp.marshal_with(provider_info_model)
    @models_bp.doc('get_provider_info')
    def get(self, provider):
        """Get information about a specific provider"""
        try:
            # Create a temporary LLM analyzer to get provider info
            analyzer = LLMAnalyzer({'llm_enabled': True})
            
            available_providers = analyzer.get_available_providers()
            available = provider in available_providers
            
            if available:
                models_list = analyzer.get_available_models(provider).get(provider, [])
            else:
                models_list = []
            
            return {
                'success': True,
                'provider': provider,
                'models': models_list,
                'available': available
            }
            
        except Exception as e:
            return {
                'success': False,
                'provider': provider,
                'models': [],
                'available': False,
                'error': str(e)
            }
