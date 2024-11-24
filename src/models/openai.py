import logging
from typing import Optional
import openai
from .llm_manager import BaseLLMClient

class OpenAIClient(BaseLLMClient):
    """OpenAI API client"""
    
    def __init__(self, api_key: str, model_name: Optional[str] = None):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key
            model_name: Model to use (e.g., 'gpt-4', 'gpt-3.5-turbo')
        """
        self.api_key = api_key
        self.model_name = model_name or "gpt-4"
        openai.api_key = api_key
        
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate response from OpenAI model
        
        Args:
            prompt: Prompt to send to model
            **kwargs: Additional parameters for API call
            
        Returns:
            Model response text
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Error generating OpenAI response: {str(e)}")
            raise
            
    def validate_api_key(self) -> bool:
        """Validate OpenAI API key"""
        try:
            # Try a simple API call
            openai.Model.list()
            return True
        except:
            return False
