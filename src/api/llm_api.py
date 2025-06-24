"""
LLM integration for analyzing screenshots
"""
import base64
import io
import os
from typing import Optional, Dict, Any, List, Tuple
from PIL import Image


class LLMAnalyzer:
    """Handles AI-powered analysis of screenshots"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._clients = {}
        self._setup_clients()
    
    @property
    def llm_enabled(self) -> bool:
        """Check if LLM is enabled"""
        return self.config.get('llm_enabled', False)
    
    @property
    def llm_prompt(self) -> str:
        """Get LLM prompt"""
        return self.config.get('llm_prompt', 'Describe what you see in this screenshot.')
    
    @property
    def llm_model(self) -> str:
        """Get LLM model"""
        return self.config.get('llm_model', 'gpt-4')
    
    def _setup_clients(self):
        """Setup all available LLM clients based on configuration"""
        if not self.llm_enabled:
            return
        
        # Setup Azure AI client
        try:
            self._setup_azure_client()
        except Exception as e:
            print(f"Azure AI setup failed: {e}")
        
        # Setup GitHub Models client
        try:
            self._setup_github_client()
        except Exception as e:
            print(f"GitHub Models setup failed: {e}")
        
        # Setup OpenAI client
        try:
            self._setup_openai_client()
        except Exception as e:
            print(f"OpenAI setup failed: {e}")
        
        if not self._clients:
            print("⚠️  LLM analysis disabled - no valid clients configured")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self._clients.keys())
    
    def get_available_models(self, provider: str = None) -> Dict[str, List[str]]:
        """Get available models for each provider or specific provider"""
        models = {}
        
        if provider:
            if provider in self._clients:
                models[provider] = self._get_models_for_provider(provider)
            return models
        
        for provider_name in self._clients.keys():
            models[provider_name] = self._get_models_for_provider(provider_name)
        
        return models
    
    def _get_models_for_provider(self, provider: str) -> List[str]:
        """Get models for a specific provider"""
        if provider == 'azure':
            azure_models = os.getenv('AZURE_AI_MODELS', 'gpt-4o,gpt-4o-mini')
            return [model.strip() for model in azure_models.split(',')]
        elif provider == 'github':
            github_models = os.getenv('GITHUB_MODELS', 'o3,o4-mini')
            return [model.strip() for model in github_models.split(',')]
        elif provider == 'openai':
            return ['gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini']
        return []
    
    def _setup_azure_client(self):
        """Setup Azure AI client"""
        try:
            # Try to import Azure AI packages
            from azure.ai.inference import ChatCompletionsClient
            from azure.core.credentials import AzureKeyCredential
            
            # Use the same environment variables as the working notebook code
            azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            azure_api_version = os.getenv("OPENAI_API_VERSION", "2023-07-01-preview")
            model = os.getenv("LLM_MODEL", "gpt-35-turbo")

            if azure_endpoint and azure_api_key:
                # Create endpoint URL with deployment name (matching working notebook)
                endpoint_url = f"{azure_endpoint}/openai/deployments/{model}"
                
                client = ChatCompletionsClient(
                    endpoint=endpoint_url,
                    credential=AzureKeyCredential(azure_api_key),
                    api_version=azure_api_version
                )
                self._clients['azure'] = client
                print(f"🤖 Azure AI client initialized - Endpoint: {endpoint_url}")
            else:
                raise ValueError("Azure OpenAI credentials not found (AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT)")
                
        except ImportError as e:
            raise ValueError(f"Azure AI packages not installed: {e}")
        except Exception as e:
            raise ValueError(f"Azure AI setup failed: {e}")
    
    def _setup_github_client(self):
        """Setup GitHub Models client"""
        try:
            from azure.ai.inference import ChatCompletionsClient
            from azure.core.credentials import AzureKeyCredential
            
            github_token = os.getenv('GITHUB_MODEL_TOKEN')
            if not github_token:
                raise ValueError("GitHub Model token not found")

            # Use the same endpoint and API version as working notebook
            azure_api_version = os.getenv("OPENAI_API_VERSION", "2023-07-01-preview")
            
            client = ChatCompletionsClient(
                endpoint="https://models.inference.ai.azure.com",
                credential=AzureKeyCredential(github_token),
                api_version=azure_api_version
            )
            self._clients['github'] = client
            print("🤖 GitHub Models client initialized")
            
        except ImportError as e:
            raise ValueError(f"Azure AI packages not installed (required for GitHub Models): {e}")
        except Exception as e:
            raise ValueError(f"GitHub Models setup failed: {e}")
    
    def _setup_openai_client(self):
        """Setup OpenAI client"""
        try:
            import openai
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not found")
            
            client = openai.OpenAI(api_key=api_key)
            self._clients['openai'] = client
            print("🤖 OpenAI client initialized")
            
        except ImportError:
            raise ValueError("OpenAI package not installed")
    
    def preprocess_image(self, image_path: str) -> Optional[Image.Image]:
        """
        Validate if the image is suitable for processing.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image.Image: Processed image if valid, None otherwise
        """
        try:
            with Image.open(image_path) as img:
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                max_dimension = 2048
                if img.width > max_dimension or img.height > max_dimension:
                    ratio = min(max_dimension / img.width, max_dimension / img.height)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='PNG', quality=85)
                img_byte_arr.seek(0)
                
                return Image.open(img_byte_arr)

        except Exception as e:
            print(f"Image preprocessing failed for {image_path}: {str(e)}")
            return None

    def encode_image(self, image_path: str) -> Optional[str]:
        """Encode image as base64 with proper validation and preprocessing."""
        try:
            processed_img = self.preprocess_image(image_path)
            if processed_img is None:
                return None

            img_byte_arr = io.BytesIO()
            processed_img.save(img_byte_arr, format='PNG', quality=85)
            img_byte_arr.seek(0)
            base64_encoded = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')

            try:
                base64.b64decode(base64_encoded)
                return base64_encoded
            except Exception as e:
                print(f"Base64 validation failed for {image_path}: {str(e)}")
                return None

        except Exception as e:
            print(f"Image encoding failed for {image_path}: {str(e)}")
            return None

    def analyze_image(self, image_data: bytes, custom_prompt: str = None, 
                     provider: str = None, model: str = None) -> Optional[str]:
        """Analyze an image with AI"""
        if not self._clients or not self.llm_enabled:
            return None
        
        # Determine which provider to use
        if provider and provider not in self._clients:
            print(f"Provider '{provider}' not available")
            return None
        
        if not provider:
            # Use first available provider
            provider = next(iter(self._clients.keys()))
        
        try:
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Use custom prompt or default
            prompt = custom_prompt or self.llm_prompt
            
            if provider == 'azure':
                return self._analyze_with_azure(image_base64, prompt, model)
            elif provider == 'github':
                return self._analyze_with_github(image_base64, prompt, model)
            elif provider == 'openai':
                return self._analyze_with_openai(image_base64, prompt, model)
            else:
                return None
                
        except Exception as e:
            print(f"Error analyzing image with {provider}: {e}")
            return None
    
    def _analyze_with_azure(self, image_base64: str, prompt: str, model: str = None) -> Optional[str]:
        """Analyze image using Azure AI"""
        try:
            from azure.ai.inference.models import (
                SystemMessage,
                UserMessage,
                TextContentItem,
                ImageContentItem,
                ImageUrl,
                ImageDetailLevel,
            )
            
            client = self._clients['azure']
            
            # Create message with image content
            messages = [
                SystemMessage("You are an AI assistant that analyzes screenshots and describes them in detail."),
                UserMessage([
                    TextContentItem(text=prompt),
                    ImageContentItem(
                        image_url=ImageUrl(
                            url=f"data:image/png;base64,{image_base64}",
                            detail=ImageDetailLevel.HIGH,
                        ),
                    ),
                ]),
            ]
            
            kwargs = {
                'messages': messages,
                'max_tokens': 500,
                'temperature': 0.3
            }
            
            # Add model if specified
            if model:
                kwargs['model'] = model
            
            response = client.complete(**kwargs)
            
            if response.choices:
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Azure AI analysis error: {e}")
        
        return None
    
    def _analyze_with_github(self, image_base64: str, prompt: str, model: str = None) -> Optional[str]:
        """Analyze image using GitHub Models"""
        try:
            from azure.ai.inference.models import (
                SystemMessage,
                UserMessage,
                TextContentItem,
                ImageContentItem,
                ImageUrl,
                ImageDetailLevel,
            )
            
            client = self._clients['github']
            
            # Create message with image content
            messages = [
                SystemMessage("You are an AI assistant that analyzes screenshots and describes them in detail."),
                UserMessage([
                    TextContentItem(text=prompt),
                    ImageContentItem(
                        image_url=ImageUrl(
                            url=f"data:image/png;base64,{image_base64}",
                            detail=ImageDetailLevel.HIGH,
                        ),
                    ),
                ]),
            ]
            
            # Use default model if not specified
            if not model:
                available_models = self._get_models_for_provider('github')
                model = available_models[0] if available_models else 'o4-mini'
            
            response = client.complete(
                messages=messages,
                model=model,
            )
            
            if response.choices:
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"GitHub Models analysis error: {e}")
        
        return None
    
    def _analyze_with_openai(self, image_base64: str, prompt: str, model: str = None) -> Optional[str]:
        """Analyze image using OpenAI"""
        try:
            client = self._clients['openai']
            
            # Use default model if not specified
            if not model:
                model = self.llm_model
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            if response.choices:
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI analysis error: {e}")
        
        return None
    
    def is_available(self) -> bool:
        """Check if LLM analysis is available"""
        return bool(self._clients) and self.llm_enabled
    
    def analyze_image_from_path(self, image_path: str, custom_prompt: str = None, 
                               provider: str = None, model: str = None) -> Optional[str]:
        """Analyze an image file with AI"""
        if not self._clients or not self.llm_enabled:
            return None
        
        # Determine which provider to use
        if provider and provider not in self._clients:
            print(f"Provider '{provider}' not available")
            return None
        
        if not provider:
            # Use first available provider
            provider = next(iter(self._clients.keys()))
        
        try:
            # Encode image from file path
            image_base64 = self.encode_image(image_path)
            if not image_base64:
                return None
            
            # Use custom prompt or default
            prompt = custom_prompt or self.llm_prompt
            
            if provider == 'azure':
                return self._analyze_with_azure(image_base64, prompt, model)
            elif provider == 'github':
                return self._analyze_with_github(image_base64, prompt, model)
            elif provider == 'openai':
                return self._analyze_with_openai(image_base64, prompt, model)
            else:
                return None
                
        except Exception as e:
            print(f"Error analyzing image from path with {provider}: {e}")
            return None
