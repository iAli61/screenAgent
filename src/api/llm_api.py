"""
LLM integration for analyzing screenshots
"""
import base64
import io
from typing import Optional

from ..core.config import Config


class LLMAnalyzer:
    """Handles AI-powered analysis of screenshots"""
    
    def __init__(self, config: Config):
        self.config = config
        self._client = None
        self._setup_client()
    
    def _setup_client(self):
        """Setup the LLM client based on configuration"""
        if not self.config.llm_enabled:
            return
        
        try:
            # Try Azure AI first
            self._setup_azure_client()
        except Exception as e:
            print(f"Azure AI setup failed: {e}")
            try:
                # Fallback to OpenAI
                self._setup_openai_client()
            except Exception as e:
                print(f"OpenAI setup failed: {e}")
                print("⚠️  LLM analysis disabled - no valid client configured")
    
    def _setup_azure_client(self):
        """Setup Azure AI client"""
        try:
            import os
            # Try to import Azure AI packages
            from azure.ai.inference import ChatCompletionsClient
            from azure.core.credentials import AzureKeyCredential
            
            endpoint = os.getenv('AZURE_AI_ENDPOINT')
            api_key = os.getenv('AZURE_AI_API_KEY')
            
            if endpoint and api_key:
                self._client = ChatCompletionsClient(
                    endpoint=endpoint,
                    credential=AzureKeyCredential(api_key)
                )
                self._client_type = 'azure'
                print("🤖 Azure AI client initialized")
            else:
                raise ValueError("Azure AI credentials not found")
                
        except ImportError as e:
            raise ValueError(f"Azure AI packages not installed: {e}")
        except Exception as e:
            raise ValueError(f"Azure AI setup failed: {e}")
    
    def _setup_openai_client(self):
        """Setup OpenAI client"""
        try:
            import os
            import openai
            
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not found")
            
            self._client = openai.OpenAI(api_key=api_key)
            self._client_type = 'openai'
            print("🤖 OpenAI client initialized")
            
        except ImportError:
            raise ValueError("OpenAI package not installed")
    
    def analyze_image(self, image_data: bytes, custom_prompt: str = None) -> Optional[str]:
        """Analyze an image with AI"""
        if not self._client or not self.config.llm_enabled:
            return None
        
        try:
            # Convert image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Use custom prompt or default
            prompt = custom_prompt or self.config.llm_prompt
            
            if self._client_type == 'azure':
                return self._analyze_with_azure(image_base64, prompt)
            elif self._client_type == 'openai':
                return self._analyze_with_openai(image_base64, prompt)
            else:
                return None
                
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return None
    
    def _analyze_with_azure(self, image_base64: str, prompt: str) -> Optional[str]:
        """Analyze image using Azure AI"""
        try:
            from azure.ai.inference.models import ChatCompletionsMessage, ChatCompletionsMessageContentItem
            
            # Create message with image content
            messages = [
                ChatCompletionsMessage(
                    role="user",
                    content=[
                        ChatCompletionsMessageContentItem(
                            type="text",
                            text=prompt
                        ),
                        ChatCompletionsMessageContentItem(
                            type="image_url",
                            image_url={
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        )
                    ]
                )
            ]
            
            response = self._client.complete(
                model=self.config.llm_model,
                messages=messages,
                max_tokens=500,
                temperature=0.3
            )
            
            if response.choices:
                return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Azure AI analysis error: {e}")
        
        return None
    
    def _analyze_with_openai(self, image_base64: str, prompt: str) -> Optional[str]:
        """Analyze image using OpenAI"""
        try:
            response = self._client.chat.completions.create(
                model=self.config.llm_model,
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
        return self._client is not None and self.config.llm_enabled
