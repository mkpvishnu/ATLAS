from flask import Flask, request, jsonify
import logging
from evaluator.registry import EvaluatorRegistry

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

DEFAULT_EVALUATIONS = 5

@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json
        logging.info("Received evaluation request")
        
        if not data.get('content'):
            logging.error("No content provided")
            return jsonify({"error": "No content provided"}), 400
            
        num_evaluations = data.get('num_evaluations', DEFAULT_EVALUATIONS)
        task_type = data.get('task_type', 'conversation_evaluation')
        
        try:
            evaluator = EvaluatorRegistry.get_evaluator(
                task_type=task_type,
                num_evaluations=num_evaluations
            )
        except ValueError as e:
            logging.error(str(e))
            return jsonify({"error": str(e)}), 400
            
        results = evaluator.evaluate(data['content'])
        
        logging.info(f"Evaluation completed successfully for task type: {task_type}")
        return jsonify(results)
        
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
