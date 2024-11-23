import json
import logging
from pathlib import Path
from typing import Dict, List
from config.config_manager import config_manager

class PromptGenerator:
    """Generates evaluation prompts based on task type and content"""
    
    def __init__(self):
        pass

    def generate_prompt(self, task_type: str, content: str) -> str:
        """
        Generate evaluation prompt based on task type and content
        
        Args:
            task_type: Type of task to evaluate
            content: Content to evaluate
            
        Returns:
            Generated prompt string
        """
        try:
            task_config = config_manager.get_task_config(task_type)
            
            # Start with the system prompt
            prompt = task_config["system_prompt"] + "\n\n"
            prompt += "Evaluate based on these criteria:\n"
            
            # Add metric descriptions with weights and scoring criteria
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
                prompt += f"{metric.upper()}_JUSTIFICATION: [detailed explanation]\n"
            
            logging.debug(f"Generated prompt for task type {task_type}")
            return prompt
            
        except Exception as e:
            logging.error(f"Error generating prompt: {str(e)}")
            raise ValueError(f"Failed to generate prompt: {str(e)}")
