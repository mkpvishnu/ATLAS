from .cloudverse import CloudverseLLMClient
from .openai import OpenAILLMClient
from .anthropic import AnthropicClient

class ModelFactory:
    @staticmethod
    def get_client(provider, token, model_name):
        if provider == 'cloudverse':
            return CloudverseClient(token, model_name)
        elif provider == 'openai':
            return OpenAILLMClient(token, model_name)
        elif provider == 'anthropic':
            return AnthropicClient(token, model_name)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
