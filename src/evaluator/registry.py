import logging
from typing import Dict, Optional
from .evaluator import Evaluator

class EvaluatorRegistry:
    _supported_task_types = {
        "conversation_evaluation",
        "code_quality_evaluation",
        "content_writing"
        # Add more task types here
    }

    @classmethod
    def get_evaluator(cls, task_type: Optional[str] = None, num_evaluations: int = 5, model_name: Optional[str] = None) -> Evaluator:
        """
        Get an evaluator instance
        
        Args:
            task_type: Type of evaluation task (optional)
            num_evaluations: Number of evaluations to perform
            model_name: Override default model name (optional)
            
        Returns:
            Evaluator instance
        """
        if task_type and task_type not in cls._supported_task_types:
            raise ValueError(f"Unsupported task type: {task_type}")
        try:
            return Evaluator(
                task_type=task_type,
                num_evaluations=num_evaluations,
                model_name=model_name
            )
        except Exception as e:
            logging.error(f"Error creating evaluator: {str(e)}")
            raise ValueError(f"Failed to create evaluator: {str(e)}")

    @classmethod
    def register_task_type(cls, task_type: str):
        """Register a new task type"""
        cls._supported_task_types.add(task_type)
        logging.info(f"Registered new task type: {task_type}")
