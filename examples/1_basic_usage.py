from atlas.evaluator import Evaluator
import os

def main():
    """Basic usage example with default settings"""
    
    # Initialize evaluator with default settings
    evaluator = Evaluator(
        task_type="writing_quality",  # Optional, will auto-detect if not provided
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Content to evaluate
    content = """
    The quick brown fox jumps over the lazy dog.
    This is a sample text that we want to evaluate for quality.
    """
    
    # Evaluate content
    result = evaluator.evaluate(content)
    
    # Print results
    print("\nEvaluation Results:")
    print("==================")
    print(f"Task Type: {result['evaluation_metadata']['task_type']}")
    print(f"Final Score: {result['final_score']}")
    print(f"Confidence: {result['confidence']}")
    
    print("\nMetric Scores:")
    for metric, score in result['metric_scores'].items():
        print(f"{metric}: {score}")

if __name__ == "__main__":
    main()
