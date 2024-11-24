from typing import Dict, Optional
from ..config.models import EvaluationConfig
from ..config.config_manager import config_manager

class PromptGenerator:
    """Generates evaluation prompts based on task type and content"""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        
    def generate_prompt(self, content: str) -> str:
        """
        Generate evaluation prompt based on task type and content
        
        Args:
            content: Content to evaluate
            
        Returns:
            Generated prompt string
        """
        try:
            task_type = self.config.task_type
            task_config = config_manager.get_task_config(task_type)
            
            # Start with the system prompt
            prompt = task_config["system_prompt"] + "\n\n"
            prompt += "Evaluate based on these criteria:\n"
            
            # Add metric descriptions with weights
            for metric, weight in task_config["weightages"].items():
                try:
                    metric_config = config_manager.get_metrics_config(metric)
                    weight_percentage = int(weight * 100)
                    
                    prompt += f"\n{metric.upper()} ({weight_percentage}%):\n"
                    prompt += f"Description: {metric_config['description']}\n"
                    
                    # Add scoring criteria if available
                    if "scoring_criteria" in metric_config:
                        prompt += "Scoring guide:\n"
                        for score, desc in metric_config["scoring_criteria"].items():
                            prompt += f"  {score}: {desc}\n"
                            
                except ValueError as e:
                    logging.warning(f"Could not find config for metric {metric}: {str(e)}")
                    continue
            
            # Add content section
            prompt += f"\nContent to evaluate:\n{content}\n\n"
            
            # Add response format instructions
            prompt += "Provide your evaluation in the following format exactly:\n"
            for metric in task_config["weightages"].keys():
                prompt += f"{metric.upper()}_SCORE: [score between 0-10]\n"
                if self.config.include_justification:
                    prompt += f"{metric.upper()}_JUSTIFICATION: [detailed explanation]\n"
            
            return prompt
            
        except Exception as e:
            logging.error(f"Error generating prompt: {str(e)}")
            raise ValueError(f"Failed to generate prompt: {str(e)}")
            
    @staticmethod
    def get_default_system_prompt(task_type: str) -> str:
        """Get the default system prompt for a task type"""
        return f"""You are an expert evaluator specialized in assessing {task_type}. 
        Your task is to evaluate the given content based on the specified criteria.
        Provide numerical scores and, if requested, detailed justifications for each metric."""
