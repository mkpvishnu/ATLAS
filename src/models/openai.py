import logging
from typing import Optional, Dict, Any
import openai

from .llm_manager import BaseLLMClient

class OpenAILLMClient(BaseLLMClient):
    """OpenAI LLM client implementation"""
    
    def __init__(
        self,
        api_key: str,
        model_name: Optional[str] = None,
        system_instruction: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key
            model_name: Optional model name to use
            system_instruction: Optional system instruction for the LLM
            **kwargs: Additional configuration parameters
        """
        self.api_key = api_key
        self.model_name = model_name or "gpt-3.5-turbo"
        self.system_instruction = system_instruction
        self.config = kwargs
        
        # Configure OpenAI
        openai.api_key = api_key
        
        logging.info(f"Initialized OpenAI client with model: {self.model_name}")
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response from OpenAI LLM
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response text
            
        Raises:
            Exception: If API call fails
        """
        try:
            # Merge configs
            params = self.config.copy()
            params.update(kwargs)
            
            # Prepare messages
            messages = []
            if self.system_instruction:
                messages.append({
                    "role": "system",
                    "content": self.system_instruction
                })
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # Make API call
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=messages,
                **params
            )
            
            # Extract and return text
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Error generating response: {str(e)}")
            raise
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate OpenAI API key
        
        Args:
            api_key: API key to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Store current key
            current_key = openai.api_key
            
            # Try validation
            openai.api_key = api_key
            models = openai.Model.list()
            valid = len(models.data) > 0
            
            # Restore key
            openai.api_key = current_key
            
            return valid
            
        except Exception as e:
            logging.error(f"Error validating API key: {str(e)}")
            return False
