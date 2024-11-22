from dotenv import load_dotenv
import os

load_dotenv()

class APIConfig:
    CLOUDVERSE_CONFIG = {
        "token": os.getenv("CLOUDVERSE"),  # Should be loaded from environment variable
        "model_name": "Azure-GPT-4o-mini",
        "api_url": "https://cloudverse.freshworkscorp.com/api/chat",
        "default_params": {
            "max_tokens": 12096,
            "temperature": 0,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
    }
