"""
Prompts API Blueprint
Manages AI analysis prompts configuration
"""
import json
import os
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields

# Create namespace
prompts_bp = Namespace('prompts', description='AI Analysis Prompts Management')

# Define API models
prompt_model = prompts_bp.model('Prompt', {
    'id': fields.String(required=True, description='Prompt identifier'),
    'name': fields.String(required=True, description='Display name'),
    'text': fields.String(required=True, description='Prompt text'),
    'description': fields.String(description='Prompt description')
})

prompts_response_model = prompts_bp.model('PromptsResponse', {
    'prompts': fields.Raw(description='Dictionary of prompts')
})

prompt_update_model = prompts_bp.model('PromptUpdate', {
    'text': fields.String(required=True, description='Updated prompt text'),
    'name': fields.String(description='Updated display name'),
    'description': fields.String(description='Updated description')
})


class PromptsService:
    """Service for managing prompts configuration"""
    
    def __init__(self):
        self.config_path = os.path.join('config', 'prompts', 'image_analysis.json')
        self._ensure_config_exists()
    
    def _ensure_config_exists(self):
        """Ensure the prompts configuration file exists"""
        if not os.path.exists(self.config_path):
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            default_config = {
                "prompts": {
                    "general": {
                        "id": "general",
                        "name": "📝 General Description",
                        "text": "Describe what you see in this screenshot in detail.",
                        "description": "A general description of the screenshot content"
                    }
                }
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
    
    def get_prompts(self):
        """Get all prompts from configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('prompts', {})
        except Exception as e:
            print(f"Error reading prompts config: {e}")
            return {}
    
    def update_prompt(self, prompt_id: str, updates: dict):
        """Update a specific prompt"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'prompts' not in config:
                config['prompts'] = {}
            
            if prompt_id not in config['prompts']:
                config['prompts'][prompt_id] = {
                    'id': prompt_id,
                    'name': updates.get('name', f'Prompt {prompt_id}'),
                    'text': updates.get('text', ''),
                    'description': updates.get('description', '')
                }
            else:
                # Update existing prompt
                prompt = config['prompts'][prompt_id]
                if 'text' in updates:
                    prompt['text'] = updates['text']
                if 'name' in updates:
                    prompt['name'] = updates['name']
                if 'description' in updates:
                    prompt['description'] = updates['description']
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            return config['prompts'][prompt_id]
        
        except Exception as e:
            print(f"Error updating prompt {prompt_id}: {e}")
            raise
    
    def get_prompt(self, prompt_id: str):
        """Get a specific prompt"""
        prompts = self.get_prompts()
        return prompts.get(prompt_id)


# Initialize service
prompts_service = PromptsService()


@prompts_bp.route('/')
class PromptsResource(Resource):
    @prompts_bp.marshal_with(prompts_response_model)
    @prompts_bp.doc('get_prompts')
    def get(self):
        """Get all AI analysis prompts"""
        try:
            prompts = prompts_service.get_prompts()
            return {'prompts': prompts}
        except Exception as e:
            prompts_bp.abort(500, f"Failed to get prompts: {str(e)}")


@prompts_bp.route('/<string:prompt_id>')
@prompts_bp.param('prompt_id', 'The prompt identifier')
class PromptResource(Resource):
    @prompts_bp.marshal_with(prompt_model)
    @prompts_bp.doc('get_prompt')
    def get(self, prompt_id):
        """Get a specific prompt"""
        try:
            prompt = prompts_service.get_prompt(prompt_id)
            if not prompt:
                prompts_bp.abort(404, f"Prompt '{prompt_id}' not found")
            return prompt
        except Exception as e:
            prompts_bp.abort(500, f"Failed to get prompt: {str(e)}")
    
    @prompts_bp.expect(prompt_update_model)
    @prompts_bp.marshal_with(prompt_model)
    @prompts_bp.doc('update_prompt')
    def put(self, prompt_id):
        """Update a specific prompt"""
        try:
            data = request.get_json()
            
            # Validate required fields
            if 'text' not in data:
                prompts_bp.abort(400, "Field 'text' is required")
            
            updated_prompt = prompts_service.update_prompt(prompt_id, data)
            return updated_prompt
        
        except Exception as e:
            prompts_bp.abort(500, f"Failed to update prompt: {str(e)}")
