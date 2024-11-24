from flask import Flask, request, jsonify
import logging
from evaluator.evaluator import Evaluator
from models.llm_manager import LLMManager
from evaluator.task_manager import TaskManager
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

# Initialize LLM client for task identification
try:
    api_key = get_api_key(DEFAULT_VENDOR)
    TaskManager.initialize_llm_client(DEFAULT_VENDOR, api_key)
    logging.info("Initialized LLM client for task identification")
except Exception as e:
    logging.error(f"Error initializing task identification: {str(e)}")

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
        include_justification = data.get('include_justification', True)  # Optional
        
        # Get vendor and model configuration
        vendor = request.headers.get('X-Vendor', DEFAULT_VENDOR).lower()
        model_name = request.headers.get('X-Model-Name')
        
        try:
            # Get API key for vendor
            api_key = get_api_key(vendor)
            
            # Initialize LLM client
            llm_client = LLMManager.initialize_client(
                vendor=vendor,
                api_key=api_key,
                model_name=model_name
            )
            
            # Create evaluator
            evaluator = Evaluator(
                task_type=task_type,
                num_evaluations=num_evaluations,
                include_justification=include_justification
            )
            
            # Perform evaluation
            result = evaluator.evaluate(content, llm_client)
            
            return result
            
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
    app.run(debug=True)
