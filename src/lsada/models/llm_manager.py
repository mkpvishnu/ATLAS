from abc import ABC, abstractmethod
import logging
from typing import Dict, Optional, Any

class BaseLLMClient(ABC):
    """Abstract base class for LLM clients"""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key"""
        pass

class LLMManager:
    """Manager class for LLM clients"""
    
    # Registry of supported vendors and their client classes
    _supported_vendors = {
        "cloudverse": "CloudverseLLMClient",
        "openai": "OpenAILLMClient"
    }
    
    @classmethod
    def initialize_client(cls, vendor: str, api_key: str, 
                        model_name: Optional[str] = None,
                        system_instruction: Optional[str] = None,
                        **kwargs) -> BaseLLMClient:
        """Initialize an LLM client for the specified vendor"""
        try:
            vendor = vendor.lower()
            if vendor not in cls._supported_vendors:
                raise ValueError(f"Unsupported vendor: {vendor}")
            
            # Import the appropriate client class
            client_class_name = cls._supported_vendors[vendor]
            module = __import__(f"lsada.models.{vendor}", fromlist=[client_class_name])
            client_class = getattr(module, client_class_name)
            
            # Create client instance
            client = client_class(
                api_key=api_key,
                model_name=model_name,
                system_instruction=system_instruction,
                **kwargs
            )
            
            logging.info(f"Initialized {vendor} LLM client")
            return client
            
        except Exception as e:
            logging.error(f"Error initializing LLM client: {str(e)}")
            raise
    
    @staticmethod
    def get_default_params(vendor: str) -> Dict[str, Any]:
        """Get default parameters for vendor"""
        defaults = {
            "cloudverse": {
                "temperature": 0,
                "max_tokens": 12000,
                "top_p": 1,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            },
            "openai": {
                "temperature": 0.7,
                "max_tokens": 1000,
                "model": "gpt-3.5-turbo",
                "top_p": 1,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0
            }
        }
        
        vendor = vendor.lower()
        if vendor not in defaults:
            raise ValueError(f"No default parameters for vendor: {vendor}")
            
        return defaults[vendor].copy()
    
    @staticmethod
    def register_vendor(vendor_name: str, client_class_name: str) -> None:
        """Register a new vendor and its client class"""
        LLMManager._supported_vendors[vendor_name.lower()] = client_class_name
        logging.info(f"Registered new vendor: {vendor_name}")

llm_manager = LLMManager()  # Singleton instance
