from .cloudverse import CloudverseClient
from .openai_client import OpenAIClient
from .anthropic import AnthropicClient

class ModelFactory:
    @staticmethod
    def get_client(provider, token, model_name):
        if provider == 'cloudverse':
            return CloudverseClient(token, model_name)
        elif provider == 'openai':
            return OpenAIClient(token, model_name)
        elif provider == 'anthropic':
            return AnthropicClient(token, model_name)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
