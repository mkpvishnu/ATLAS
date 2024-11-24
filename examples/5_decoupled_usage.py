"""
Example demonstrating the decoupled usage of ATLAS evaluation framework.
The LLM manager can be used independently for other purposes,
and the evaluator can work with any LLM client that implements BaseLLMClient.
"""

from models.llm_manager import LLMManager
from evaluator.evaluator import Evaluator

def main():
    # Initialize LLM client
    llm_client = LLMManager.initialize_client(
        vendor="cloudverse",
        api_key="your_api_key",
        model_name="optional_model_name",
        system_instruction="You are an expert content evaluator."
    )
    
    # Create evaluator
    evaluator = Evaluator(
        task_type="conversation_evaluation",
        num_evaluations=3
    )
    
    # Content to evaluate
    content = """
    Hello! How can I assist you today?
    I'm here to help with any questions you might have.
    """
    
    # Perform evaluation
    result = evaluator.evaluate(content, llm_client)
    
    # Print results
    print("\nEvaluation Results:")
    print(f"Task Type: {result['metadata']['task_type']}")
    print(f"Number of Evaluations: {result['metadata']['num_evaluations']}")
    print("\nScores:")
    for metric, score in result['Scores'].items():
        print(f"{metric}: {score['score']}")
    
    # Example of using LLM client independently
    response = llm_client.generate_response(
        "Summarize the following text in one sentence: " + content
    )
    print("\nLLM Summary:", response)

if __name__ == "__main__":
    main()
