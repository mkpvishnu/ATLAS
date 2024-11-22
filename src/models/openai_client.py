import openai

class OpenAIClient:
    def __init__(self, token, model_name):
        self.token = token
        self.model_name = model_name
        openai.api_key = self.token
    
    def generate_response(self, prompt, max_tokens=150, temperature=0.0, top_p=1.0):
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
        return response['choices'][0]['message']['content'].strip()
