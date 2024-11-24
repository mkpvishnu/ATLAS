import logging
from typing import Optional
import requests
from .llm_manager import BaseLLMClient

class CloudverseClient(BaseLLMClient):
    """Cloudverse API client"""
    
    API_URL = "https://cloudverse.freshworkscorp.com/api/chat"
    
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        """
        Initialize Cloudverse client
        
        Args:
            api_key: Cloudverse API key
            model_name: Model to use
        """
        self.api_key = api_key
        self.model_name = model_name or "cloudverse-v1"
        
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response from Cloudverse model
        
        Args:
            prompt: Prompt to send to model
            **kwargs: Additional parameters for API call
            
        Returns:
            Model response text
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                **kwargs
            }
            
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            logging.error(f"Error generating Cloudverse response: {str(e)}")
            raise
            
    def validate_api_key(self) -> bool:
        """Validate Cloudverse API key"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            response = requests.get(
                "https://api.cloudverse.ai/v1/models",
                headers=headers
            )
            return response.status_code == 200
        except:
            return False
