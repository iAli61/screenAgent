#!/usr/bin/env python3
"""
LLM Handler - Module for processing screenshots with multimodal LLMs using Azure OpenAI
"""
import os
import base64
import io
import json
from PIL import Image
import dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from config import load_from_config, DEFAULT_LLM_ENABLED, DEFAULT_LLM_MODEL, DEFAULT_LLM_PROMPT

# Load environment variables from .env file
dotenv.load_dotenv()

import logging
from typing import Optional


def preprocess_image(image_path: str) -> Optional[Image.Image]:
    """
    Validate if the image is suitable for processing.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        bool: True if image is valid, False otherwise
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



def encode_image(image_path: str) -> Optional[str]:
    """Encode image as base64 with proper validation and preprocessing."""
    try:
        

        processed_img = preprocess_image(image_path)
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

class LLMHandler:
    """Handler for interacting with multimodal LLMs using Azure OpenAI"""
    
    def __init__(self):
        """Initialize the LLM handler"""
        # Load configuration
        self.enabled = load_from_config('llm_enabled', DEFAULT_LLM_ENABLED)
        self.model = load_from_config('llm_model', DEFAULT_LLM_MODEL)
        # Strip the "azure/" prefix if present
        if self.model.startswith("azure/"):
            self.model = self.model.replace("azure/", "")
        self.prompt = load_from_config('llm_prompt', DEFAULT_LLM_PROMPT)
        
        # Azure OpenAI configuration
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_api_version = os.getenv("AZURE_API_VERSION", "2025-01-01-preview")
        
        print(f"Azure Endpoint: {self.azure_endpoint}")
        print(f"Azure API Key available: {'Yes' if self.azure_api_key else 'No'}")
        print(f"Azure API Version: {self.azure_api_version}")
        print(f"Model deployment name: {self.model}")
        
        # Check for missing configuration
        if not self.azure_endpoint:
            print("WARNING: AZURE_OPENAI_ENDPOINT environment variable is not set. Please set it in your .env file.")
        
        # Initialize Azure OpenAI client if enabled
        self.client = None
        if self.enabled and self.azure_api_key and self.azure_endpoint:
            # Create endpoint URL with deployment name
            endpoint_url = f"{self.azure_endpoint}/openai/deployments/{self.model}"
            print(f"Endpoint URL: {endpoint_url}")
            self.client = ChatCompletionsClient(
                endpoint=endpoint_url,
                credential=AzureKeyCredential(self.azure_api_key),
                api_version=self.azure_api_version
            )
        
    def is_available(self):
        """Check if the LLM functionality is available and enabled"""
        return self.enabled and self.client is not None
    
    def get_image_base64(self, image_bytes):
        """Convert image bytes to base64 string"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def analyze_image(self, image_bytes, custom_prompt=None):
        """
        Analyze an image with the Azure OpenAI multimodal model
        
        Args:
            image_bytes: The screenshot image as bytes
            custom_prompt: Optional custom instructions for the LLM
            
        Returns:
            dict: {'success': bool, 'response': str, 'error': str (if any)}
        """
        if not self.is_available():
            return {
                'success': False, 
                'error': "Azure OpenAI functionality is not enabled or not configured properly. Check your .env file and settings."
            }
        
        try:
            # Convert image to base64
            img_base64 = self.get_image_base64(image_bytes)

            # Save the image to a temporary file
            image = Image.open(io.BytesIO(image_bytes))
            temp_image_path = "temp_image.png"
            image.save(temp_image_path)
            print(f"Image saved to {temp_image_path}")

            base64_image = encode_image(temp_image_path)

            # Use provided prompt or default
            prompt_text = custom_prompt if custom_prompt else self.prompt
            
            # Call Azure OpenAI API with the image
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Create the payload with system and user messages

                    payload = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "you are a helpful assistant that can analyze images and provide information about them."
                            },
                            {
                                "role": "user",
                                "content": [
                                            {
                                                "type": "text",
                                                "text": prompt_text
                                            },
                                            {
                                                "type": "image_url",
                                                "image_url": {
                                                    "url": f"data:image/jpeg;base64,{img_base64}"
                                                }
                                            }
                                        ]
                            }
                        ],
                        "max_tokens": 2048
                    }
                    # Call the API
                    response = self.client.complete(payload)
                    
                    print("Model:", response.model)
                    print("Usage:")
                    print("    Prompt tokens:", response.usage.prompt_tokens)
                    print("    Total tokens:", response.usage.total_tokens)
                    print("    Completion tokens:", response.usage.completion_tokens)
                    
                    result = response.choices[0].message.content
                    print("Analysis Result:", result)
                    
                    return {
                        'success': True,
                        'response': result
                    }
                    
                except Exception as api_error:
                    print(f"Attempt {attempt+1} failed: {str(api_error)}")
                    if attempt == max_retries - 1:
                        print(f"API Error Details: {str(api_error)}")
                        return {
                            'success': False,
                            'error': f"Azure OpenAI API error: {str(api_error)}"
                        }
            
        except Exception as e:
            print(f"General Error: {str(e)}")
            return {
                'success': False,
                'error': f"Azure OpenAI analysis failed: {str(e)}"
            }

# Create a singleton instance
llm_handler = LLMHandler()