import logging
from typing import Dict

class PromptGenerator:
    @staticmethod
    def format_criteria(criteria: Dict, criteria_name: str) -> str:
        return "\n".join([
            f"Score {score}: {description}"
            for score, description in criteria[criteria_name].items()
        ])

    @staticmethod
    def generate_prompt(task_type: str, content: str, criteria: Dict) -> str:
        logging.info(f"Generating prompt for task type: {task_type}")
        
        prompt_generators = {
            "conversation_evaluation": PromptGenerator.generate_conversation_evaluation_prompt,
            "code_quality_evaluation": PromptGenerator.generate_code_evaluation_prompt,
            # Add more task types here
        }
        
        generator = prompt_generators.get(task_type)
        if not generator:
            raise ValueError(f"No prompt generator found for task type: {task_type}")
            
        return generator(content, criteria)

    @staticmethod
    def generate_conversation_evaluation_prompt(content: str, criteria: Dict) -> str:
        logging.info("Generating conversation evaluation prompt")
        prompt = f"""You are an expert conversation evaluator. Evaluate the following multi-turn conversation based on these specific criteria:

1. Coherence (25 points):
{PromptGenerator.format_criteria(criteria, "coherence")}

2. Relevance (25 points):
{PromptGenerator.format_criteria(criteria, "relevance")}

3. Helpfulness (25 points):
{PromptGenerator.format_criteria(criteria, "helpfulness")}

4. Context Awareness (15 points):
{PromptGenerator.format_criteria(criteria, "context_awareness")}

5. Consistency (10 points):
{PromptGenerator.format_criteria(criteria, "consistency")}

Conversation to evaluate:
{content}

Provide your evaluation in the following format exactly:
COHERENCE_SCORE: [number]
COHERENCE_JUSTIFICATION: [text]
RELEVANCE_SCORE: [number]
RELEVANCE_JUSTIFICATION: [text]
HELPFULNESS_SCORE: [number]
HELPFULNESS_JUSTIFICATION: [text]
CONTEXT_AWARENESS_SCORE: [number]
CONTEXT_AWARENESS_JUSTIFICATION: [text]
CONSISTENCY_SCORE: [number]
CONSISTENCY_JUSTIFICATION: [text]
"""
        return prompt

    @staticmethod
    def generate_code_evaluation_prompt(content: str, criteria: Dict) -> str:
        prompt = f"""You are an expert code evaluator. Evaluate the following code based on these specific criteria:

1. Readability (25 points):
{PromptGenerator.format_criteria(criteria, "readability")}

2. Maintainability (25 points):
{PromptGenerator.format_criteria(criteria, "maintainability")}

3. Efficiency (20 points):
{PromptGenerator.format_criteria(criteria, "efficiency")}

4. Best Practices (15 points):
{PromptGenerator.format_criteria(criteria, "best_practices")}

5. Error Handling (15 points):
{PromptGenerator.format_criteria(criteria, "error_handling")}

Code to evaluate:
{content}

Provide your evaluation in the following format exactly:
READABILITY_SCORE: [number]
READABILITY_JUSTIFICATION: [text]
MAINTAINABILITY_SCORE: [number]
MAINTAINABILITY_JUSTIFICATION: [text]
EFFICIENCY_SCORE: [number]
EFFICIENCY_JUSTIFICATION: [text]
BEST_PRACTICES_SCORE: [number]
BEST_PRACTICES_JUSTIFICATION: [text]
ERROR_HANDLING_SCORE: [number]
ERROR_HANDLING_JUSTIFICATION: [text]
"""
        return prompt
