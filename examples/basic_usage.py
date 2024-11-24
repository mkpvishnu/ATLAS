from atlas.config.models import EvaluationConfig, ModelConfig
from atlas.evaluator import Evaluator
from atlas.evaluator.registry import EvaluatorRegistry
import os

def main():
    # Create model configuration
    model_config = ModelConfig(
        provider="openai",
        model_name="gpt-4",
        api_key=os.getenv("OPENAI_API_KEY")  # Load from environment variable
    )
    
    # Create evaluation configuration
    eval_config = EvaluationConfig(
        task_type="writing_quality",  # Optional, will be auto-detected if not provided
        num_evaluations=1,
        include_justification=True,  # Set to False to save tokens
        model=model_config,
        temperature=0.0
    )
    
    # Create evaluator
    registry = EvaluatorRegistry()
    evaluator = registry.get_evaluator(config=eval_config)
    
    # Content to evaluate
    content = """
    The quick brown fox jumps over the lazy dog.
    This is a sample text that we want to evaluate for quality.
    """
    
    # Perform evaluation
    result = evaluator.evaluate(content)
    
    # Print results
    print("\nEvaluation Results:")
    print("==================")
    print(f"Task Type: {result['metadata']['task_type']}")
    print(f"Overall Score: {result['total_weighted_score']:.2f}")
    print("\nDetailed Scores:")
    
    for metric, score in result['raw_scores'].items():
        print(f"\n{metric}:")
        print(f"  Score: {score}")
        if result['metadata']['include_justification']:
            print(f"  Justification: {result['justifications'][metric]}")
    
    if result['validation_issues']:
        print("\nValidation Issues:")
        for issue in result['validation_issues']:
            print(f"- {issue}")

if __name__ == "__main__":
    main()
