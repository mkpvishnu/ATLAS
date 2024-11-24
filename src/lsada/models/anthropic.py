import requests

class AnthropicClient:
    def __init__(self, token, model_name):
        self.token = token
        self.model_name = model_name
        self.api_url = 'https://api.anthropic.com/v1/complete'
    
    def generate_response(self, prompt, max_tokens=150, temperature=0.0, top_p=1.0):
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.token
        }
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        }
        response = requests.post(self.api_url, headers=headers, json=data)
        if response.status_code == 200:
            res_json = response.json()
            return res_json.get('completion', '').strip()
        else:
            raise Exception(f"Anthropic API Error: {response.status_code} - {response.text}")
