from typing import Dict, Optional
import logging
from abc import ABC, abstractmethod
from enum import Enum

class ModelVendor(Enum):
    CLOUDVERSE = "cloudverse"
    OPENAI = "openai"
    
    @classmethod
    def from_str(cls, vendor: str) -> "ModelVendor":
        try:
            return cls(vendor.lower())
        except ValueError:
            raise ValueError(f"Unsupported vendor: {vendor}. Supported vendors: {[v.value for v in cls]}")

class BaseLLMClient(ABC):
    """Base class for LLM clients"""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM"""
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate API key"""
        pass

class LLMManager:
    """Manages LLM clients and configurations"""
    
    _default_params = {
        ModelVendor.CLOUDVERSE: {
            "temperature": 0,
            "max_tokens": 12000,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        },
        ModelVendor.OPENAI: {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
    }
    
    def __init__(self):
        self._clients = {}
        
    def get_client(self, vendor: str, api_key: str, model_name: Optional[str] = None) -> BaseLLMClient:
        """
        Get or create LLM client for vendor
        
        Args:
            vendor: Vendor name (e.g., 'cloudverse', 'openai')
            api_key: API key for vendor
            model_name: Optional model name
            
        Returns:
            LLM client instance
            
        Raises:
            ValueError: If vendor is not supported
        """
        vendor_enum = ModelVendor.from_str(vendor)
        
        # Create new client if needed
        if vendor_enum not in self._clients or self._clients[vendor_enum].api_key != api_key:
            client = self._create_client(vendor_enum, api_key, model_name)
            self._clients[vendor_enum] = client
            
        return self._clients[vendor_enum]
    
    def _create_client(self, vendor: ModelVendor, api_key: str, model_name: Optional[str]) -> BaseLLMClient:
        """Create new LLM client"""
        if vendor == ModelVendor.CLOUDVERSE:
            from .cloudverse import CloudverseClient
            return CloudverseClient(api_key, model_name)
        elif vendor == ModelVendor.OPENAI:
            from .openai import OpenAIClient
            return OpenAIClient(api_key, model_name)
        else:
            raise ValueError(f"Unsupported vendor: {vendor}")
    
    @classmethod
    def get_default_params(cls, vendor: str) -> Dict:
        """Get default parameters for vendor"""
        vendor_enum = ModelVendor.from_str(vendor)
        return cls._default_params[vendor_enum].copy()
    
    @classmethod
    def update_default_params(cls, vendor: str, params: Dict) -> None:
        """Update default parameters for vendor"""
        vendor_enum = ModelVendor.from_str(vendor)
        cls._default_params[vendor_enum].update(params)
        
llm_manager = LLMManager()  # Singleton instance
