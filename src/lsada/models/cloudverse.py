import logging
from typing import Optional, Dict, Any
import requests

from .llm_manager import BaseLLMClient, LLMManager

class CloudverseLLMClient(BaseLLMClient):
    """Cloudverse LLM client implementation"""
    
    API_BASE = "https://cloudverse.freshworkscorp.com/api/chat"
    
    def __init__(
        self,
        api_key: str,
        model_name: Optional[str] = None,
        system_instruction: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Cloudverse client
        
        Args:
            api_key: Cloudverse API key
            model_name: Optional model name to use
            system_instruction: Optional system instruction for the LLM
            **kwargs: Additional configuration parameters
        """
        self.api_key = api_key
        self.model_name = model_name or "Azure-GPT-4o-mini"
        self.system_instruction = system_instruction
        
        # Get default parameters and update with any provided kwargs
        self.config = LLMManager.get_default_params("cloudverse")
        self.config.update(kwargs)
        
        # Set up session
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": api_key,
            "Content-Type": "application/json"
        })
        
        logging.info(f"Initialized Cloudverse client with model: {self.model_name}")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response from Cloudverse LLM
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Merge configs with any provided kwargs
            params = self.config.copy()
            params.update(kwargs)
            
            # Prepare request
            payload = {
                "model": self.model_name,
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                "temperature": params.get("temperature", 0),
                "max_tokens": params.get("max_tokens", 12000),
                "top_p": params.get("top_p", 1),
                "frequency_penalty": params.get("frequency_penalty", 0),
                "presence_penalty": params.get("presence_penalty", 0)
            }
            
            # Add system instruction if provided
            if self.system_instruction:
                payload["system_instructions"] = self.system_instruction
            
            # Make API call
            response = self.session.post(
                self.API_BASE,
                json=payload
            )
            response.raise_for_status()
            
            # Extract and return text
            result = response.json()
            return result
            
        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            raise
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate Cloudverse API key
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Try a simple request to validate
            response = self.session.post(
                self.API_BASE,
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1
                }
            )
            return response.status_code == 200
            
        except Exception as e:
            logging.error(f"Error validating API key: {str(e)}")
            return False
