import logging
from typing import Dict, Optional
from .evaluator import Evaluator

class EvaluatorRegistry:
    """Registry for evaluator instances"""
    
    _instances: Dict[str, Evaluator] = {}
    
    @classmethod
    def get_evaluator(
        cls,
        task_type: Optional[str] = None,
        num_evaluations: int = 1,
        vendor: str = "cloudverse",
        api_key: str = None,
        model_name: Optional[str] = None
    ) -> Evaluator:
        """
        Get or create evaluator instance
        
        Args:
            task_type: Type of task to evaluate
            num_evaluations: Number of evaluations to perform
            vendor: LLM vendor to use
            api_key: API key for vendor
            model_name: Name of model to use
            
        Returns:
            Evaluator instance
            
        Raises:
            ValueError: If required parameters are missing
        """
        # Validate API key
        if not api_key:
            raise ValueError("API key is required")
            
        # Create instance key
        instance_key = f"{vendor}:{model_name or 'default'}:{task_type or 'default'}"
        
        # Create new instance if needed
        if instance_key not in cls._instances:
            logging.info(f"Creating new evaluator instance for {instance_key}")
            cls._instances[instance_key] = Evaluator(
                task_type=task_type,
                num_evaluations=num_evaluations,
                vendor=vendor,
                api_key=api_key,
                model_name=model_name
            )
            
        return cls._instances[instance_key]
        
    @classmethod
    def clear_instances(cls) -> None:
        """Clear all evaluator instances"""
        cls._instances.clear()
