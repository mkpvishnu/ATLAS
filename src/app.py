from flask import Flask, request, jsonify
import logging
from evaluator.registry import EvaluatorRegistry
from dotenv import load_dotenv
import os

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

DEFAULT_EVALUATIONS = 5
DEFAULT_VENDOR = "cloudverse"

# Load environment variables
load_dotenv()

def get_api_key(vendor: str) -> str:
    """Get API key for vendor from environment variables"""
    key_mapping = {
        "cloudverse": "CLOUDVERSE_API_KEY",
        "openai": "OPENAI_API_KEY"
    }
    
    env_key = key_mapping.get(vendor.lower())
    if not env_key:
        raise ValueError(f"Unsupported vendor: {vendor}")
        
    api_key = os.getenv(env_key)
    if not api_key:
        raise ValueError(f"API key not found for vendor: {vendor}")
        
    return api_key

@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json
        logging.info("Received evaluation request")
        
        # Validate content
        if 'content' not in data:
            return jsonify({"error": "No content provided"}), 400
            
        # Get evaluation parameters
        content = data['content']
        num_evaluations = data.get('num_evaluations', DEFAULT_EVALUATIONS)
        task_type = data.get('task_type')  # Optional
        prompt = data.get('prompt')  # Optional
        
        # Get vendor and model configuration
        vendor = request.headers.get('X-Vendor', DEFAULT_VENDOR).lower()
        model_name = request.headers.get('X-Model-Name')
        
        try:
            # Get API key for vendor
            print(vendor)
            api_key = get_api_key(vendor)
            
            # Create evaluator
            evaluator = EvaluatorRegistry.get_evaluator(
                task_type=task_type,
                num_evaluations=num_evaluations,
                vendor=vendor,
                api_key=api_key,
                model_name=model_name
            )
            
            # Perform evaluation
            result = evaluator.evaluate(content)
            
            return jsonify(result)
            
        except ValueError as e:
            logging.error(str(e))
            return jsonify({"error": str(e)}), 400
            
    except Exception as e:
        logging.error(f"Error in evaluation endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
