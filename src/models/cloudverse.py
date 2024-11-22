import requests
import json
import logging
from typing import Dict, Optional

class CloudverseClient:
    """Client for interacting with the Cloudverse API"""
    
    def __init__(self, token: str, model_name: str, api_url: Optional[str] = None):
        """
        Initialize the Cloudverse client
        
        Args:
            token: Authentication token
            model_name: Name of the model to use
            api_url: Optional API URL override
        """
        self.token = token

        self.model_name = model_name
        self.api_url = api_url or 'https://cloudverse.freshworkscorp.com/api/chat'
        logging.info(f"Initialized CloudverseClient with model: {model_name}, token: {token}")

    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the Cloudverse API
        
        Args:
            prompt: The input prompt
            **kwargs: Additional parameters for the API call (temperature, max_tokens, etc.)
        
        Returns:
            str: The generated response text
            
        Raises:
            Exception: If the API call fails
        """
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.token}'
            }

            logging.info(f"API Headers: {headers}")
            # Prepare the request payload
            data = {
                "model": self.model_name,
                "messages": [{
                    "content": prompt,
                    "role": "user"
                }],
                "system_instructions": "You are an AI assistant that helps evaluate content."
            }
            
            # Update with any additional parameters
            data.update(kwargs)
            logging.debug(f"Making API request to {self.api_url}")
            logging.info(f"API Request Data: {data}")
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=data, 
                verify=False
            )
            
            # Log the response for debugging
            logging.info(f"API Response: {response.json()}")
            
            if response.status_code == 200:
                return response.json()
            else:
                error_msg = f"Cloudverse API Error: {response.status_code} - {response.text}"
                logging.error(error_msg)
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error while calling Cloudverse API: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in Cloudverse API call: {str(e)}"
            logging.error(error_msg)
            raise
    
    # def _parse_response(self, response_text: str) -> str:
    #     """
    #     Parse the API response text
        
    #     Args:
    #         response_text: Raw response text from the API
            
    #     Returns:
    #         str: Parsed response content
            
    #     Raises:
    #         Exception: If parsing fails
    #     """
    #     try:
    #         res_json = json.loads(response_text)
    #         content = res_json.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            
    #         if not content:
    #             logging.warning("Empty content in API response")
    #             return ""
                
    #         return content
            
    #     except json.JSONDecodeError as e:
    #         logging.warning(f"Failed to parse JSON response: {str(e)}")
    #         # If JSON parsing fails, return the raw text
    #         return response_text.strip()
            
    #     except Exception as e:
    #         error_msg = f"Error processing API response: {str(e)}"
    #         logging.error(error_msg)
    #         raise Exception(error_msg)
