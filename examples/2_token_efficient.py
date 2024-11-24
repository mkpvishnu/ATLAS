from atlas.evaluator import Evaluator
import os

def main():
    """Example showing token-efficient evaluation"""
    
    # Initialize evaluator with token-saving settings
    evaluator = Evaluator(
        task_type="code_quality",
        include_justification=False,  # Skip justifications to save tokens
        num_evaluations=1,  # Single evaluation instead of multiple
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Code to evaluate
    code = """
    def fibonacci(n):
        if n <= 0:
            return []
        elif n == 1:
            return [0]
        
        sequence = [0, 1]
        while len(sequence) < n:
            sequence.append(sequence[-1] + sequence[-2])
        return sequence
    """
    
    # Evaluate code
    result = evaluator.evaluate(code)
    
    # Print results (scores only, no justifications)
    print("\nCode Evaluation Results:")
    print("=======================")
    print(f"Overall Score: {result['final_score']}")
    
    print("\nMetric Scores:")
    for metric, score in result['metric_scores'].items():
        print(f"{metric}: {score}")
    
    # Print token usage if available
    if "token_usage" in result["evaluation_metadata"]:
        print(f"\nToken Usage: {result['evaluation_metadata']['token_usage']}")

if __name__ == "__main__":
    main()
