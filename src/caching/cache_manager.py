import hashlib
import json
import os

class CacheManager:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _hash_input(self, inputs):
        """
        Create a unique hash for the given inputs.
        
        Args:
            inputs (dict): Input data.
        
        Returns:
            str: SHA256 hash string.
        """
        input_str = json.dumps(inputs, sort_keys=True)
        return hashlib.sha256(input_str.encode('utf-8')).hexdigest()
    
    def get_cache_path(self, inputs):
        hash_key = self._hash_input(inputs)
        return os.path.join(self.cache_dir, f"{hash_key}.json")
    
    def load_cache(self, inputs):
        path = self.get_cache_path(inputs)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return None
    
    def save_cache(self, inputs, outputs):
        path = self.get_cache_path(inputs)
        with open(path, 'w') as f:
            json.dump(outputs, f)
