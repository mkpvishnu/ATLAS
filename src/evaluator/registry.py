from typing import Dict
from .evaluator import Evaluator
import logging

class EvaluatorRegistry:
    _supported_task_types = {
        "conversation_evaluation",
        "code_quality_evaluation"
        # Add more task types here
    }

    @classmethod
    def get_evaluator(cls, task_type: str, **kwargs) -> Evaluator:
        if task_type not in cls._supported_task_types:
            raise ValueError(f"Unsupported task type: {task_type}")
        return Evaluator(task_type=task_type, **kwargs)

    @classmethod
    def register_task_type(cls, task_type: str):
        """Register a new task type"""
        cls._supported_task_types.add(task_type)
        logging.info(f"Registered new task type: {task_type}")
