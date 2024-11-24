from atlas.evaluator import Evaluator
from typing import List, Dict
import os
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

class BatchEvaluator:
    """Helper class for batch evaluation"""
    
    def __init__(self, task_type: str, max_workers: int = 3):
        self.task_type = task_type
        self.max_workers = max_workers
        self.api_key = os.getenv("OPENAI_API_KEY")
    
    def evaluate_single(self, content: str) -> Dict:
        """Evaluate a single piece of content"""
        evaluator = Evaluator(
            task_type=self.task_type,
            include_justification=True,
            num_evaluations=1,
            api_key=self.api_key
        )
        return evaluator.evaluate(content)
    
    def evaluate_batch(self, contents: List[str]) -> List[Dict]:
        """Evaluate multiple pieces of content in parallel"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self.evaluate_single, contents))
        return results

def main():
    """Example showing batch evaluation"""
    
    # Sample contents to evaluate
    contents = [
        "This is the first piece of content to evaluate.",
        "Here's another piece of content that needs evaluation.",
        "And finally, a third piece of content for testing.",
    ]
    
    # Initialize batch evaluator
    batch_evaluator = BatchEvaluator(
        task_type="writing_quality",
        max_workers=3
    )
    
    # Start timing
    start_time = datetime.now()
    
    # Evaluate all content
    results = batch_evaluator.evaluate_batch(contents)
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    
    # Print results
    print("\nBatch Evaluation Results:")
    print("========================")
    print(f"Evaluated {len(contents)} pieces of content in {duration:.2f} seconds")
    print(f"Average time per evaluation: {duration/len(contents):.2f} seconds")
    
    for i, result in enumerate(results, 1):
        print(f"\nContent {i}:")
        print(f"Final Score: {result['final_score']}")
        print("Metric Scores:")
        for metric, score in result['metric_scores'].items():
            print(f"  {metric}: {score}")
    
    # Save results to file
    output_file = "batch_evaluation_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results saved to {output_file}")

if __name__ == "__main__":
    main()
