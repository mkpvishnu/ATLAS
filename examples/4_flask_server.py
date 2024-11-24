from flask import Flask, request, jsonify
from atlas.evaluator import Evaluator
from atlas.utils.task_identifier import TaskIdentifier
import os
from typing import Dict, Optional
from datetime import datetime
import logging

app = Flask(__name__)

# Cache evaluator instances
evaluator_cache: Dict[str, Evaluator] = {}
task_identifier = TaskIdentifier()

def get_evaluator(task_type: Optional[str] = None, 
                 include_justification: bool = True,
                 num_evaluations: int = 1,
                 model_name: Optional[str] = None) -> Evaluator:
    """Get or create an evaluator instance"""
    cache_key = f"{task_type}_{include_justification}_{num_evaluations}_{model_name}"
    
    if cache_key not in evaluator_cache:
        evaluator_cache[cache_key] = Evaluator(
            task_type=task_type,
            include_justification=include_justification,
            num_evaluations=num_evaluations,
            model_name=model_name
        )
    
    return evaluator_cache[cache_key]

@app.route("/identify_task", methods=["POST"])
def identify_task():
    """Endpoint to identify task type from prompt"""
    try:
        data = request.json
        if not data or "prompt" not in data:
            return jsonify({
                "error": "Missing required field: prompt"
            }), 400
            
        # Get optional model configuration for task identifier
        model_name = data.get("identifier_model")
        
        # Identify task type from prompt
        task_type = task_identifier.identify_task_from_prompt(
            data["prompt"],
            model_name=model_name
        )
        
        return jsonify({
            "task_type": task_type,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route("/evaluate", methods=["POST"])
def evaluate():
    """Endpoint for content evaluation"""
    try:
        # Get request data
        data = request.json
        if not data or "content" not in data:
            return jsonify({
                "error": "Missing required field: content"
            }), 400
        
        # Get optional parameters
        task_type = data.get("task_type")
        prompt = data.get("prompt")
        
        # If prompt is provided but no task_type, identify task
        if prompt and not task_type:
            identifier_model = data.get("identifier_model")  # Optional different model for identification
            task_type = task_identifier.identify_task_from_prompt(prompt, model_name=identifier_model)
            logging.info(f"Identified task type from prompt: {task_type}")
        
        # Get other parameters
        include_justification = data.get("include_justification", True)
        num_evaluations = data.get("num_evaluations", 1)
        model_name = data.get("model_name")  # Model for evaluation
        
        # Get evaluator
        evaluator = get_evaluator(
            task_type=task_type,
            include_justification=include_justification,
            num_evaluations=num_evaluations,
            model_name=model_name
        )
        
        # Perform evaluation
        start_time = datetime.now()
        result = evaluator.evaluate(data["content"])
        duration = (datetime.now() - start_time).total_seconds()
        
        # Add response metadata
        if 'metadata' not in result:
            result['metadata'] = {}
            
        result['metadata'].update({
            "duration_seconds": duration,
            "timestamp": datetime.now().isoformat(),
            "request_id": request.headers.get("X-Request-ID"),
            "identified_from_prompt": prompt is not None and task_type is None,
            "task_type": task_type
        })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route("/supported_tasks", methods=["GET"])
def get_supported_tasks():
    """Get list of supported task types"""
    try:
        task_types = Evaluator.get_supported_tasks()
        return jsonify({
            "task_types": task_types,
            "default_task_type": Evaluator.get_default_task_type()
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route("/task_weights/<task_type>", methods=["GET"])
def get_task_weights(task_type: str):
    """Get weights for a specific task type"""
    try:
        weights = Evaluator.get_task_weights(task_type)
        return jsonify({
            "task_type": task_type,
            "weights": weights
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route("/default_task_type", methods=["GET", "PUT"])
def manage_default_task_type():
    """Get or set default task type"""
    try:
        if request.method == "GET":
            return jsonify({
                "default_task_type": Evaluator.get_default_task_type()
            })
        
        # Handle PUT request
        data = request.json
        if not data or "task_type" not in data:
            return jsonify({
                "error": "Missing required field: task_type"
            }), 400
            
        Evaluator.set_default_task_type(data["task_type"])
        return jsonify({
            "message": f"Default task type set to: {data['task_type']}",
            "default_task_type": data["task_type"]
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

if __name__ == "__main__":
    # Example usage with curl:
    """
    # Identify task type from prompt
    curl -X POST http://localhost:5000/identify_task \
        -H "Content-Type: application/json" \
        -d '{
            "prompt": "Write a story about a magical forest",
            "identifier_model": "cloudverse-v1"  # Optional
        }'
    
    # Evaluate content with explicit task type
    curl -X POST http://localhost:5000/evaluate \
        -H "Content-Type: application/json" \
        -d '{
            "content": "Once upon a time in a magical forest...",
            "task_type": "writing_quality",
            "include_justification": true,
            "num_evaluations": 1,
            "model_name": "cloudverse-v1"
        }'
    
    # Evaluate content with prompt for task identification
    curl -X POST http://localhost:5000/evaluate \
        -H "Content-Type: application/json" \
        -d '{
            "content": "Once upon a time in a magical forest...",
            "prompt": "Write a story about a magical forest",
            "identifier_model": "cloudverse-v1",  # Optional: model for task identification
            "model_name": "cloudverse-v2",        # Optional: model for evaluation
            "include_justification": true,
            "num_evaluations": 1
        }'
    
    # Get supported tasks
    curl http://localhost:5000/supported_tasks
    
    # Get task weights
    curl http://localhost:5000/task_weights/writing_quality
    
    # Get default task type
    curl http://localhost:5000/default_task_type
    
    # Set default task type
    curl -X PUT http://localhost:5000/default_task_type \
        -H "Content-Type: application/json" \
        -d '{"task_type": "writing_quality"}'
    
    # Health check
    curl http://localhost:5000/health
    """
    
    app.run(debug=True, port=5000)
