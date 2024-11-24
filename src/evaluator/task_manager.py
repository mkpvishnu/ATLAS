from typing import Dict, List, Optional
import logging
from config.config_manager import config_manager

class TaskManager:
    """Manages task types and their configurations"""
    
    _default_task_type = "conversation_evaluation"  # Class-level default task type
    
    @classmethod
    def set_default_task_type(cls, task_type: str) -> None:
        """
        Set default task type for all new evaluations
        
        Args:
            task_type: Task type to set as default
            
        Raises:
            ValueError: If task type is not supported
        """
        if task_type not in cls.get_supported_tasks():
            raise ValueError(f"Unsupported task type: {task_type}")
        cls._default_task_type = task_type
        logging.info(f"Default task type set to: {task_type}")
    
    @classmethod
    def get_default_task_type(cls) -> str:
        """
        Get current default task type
        
        Returns:
            Current default task type
        """
        return cls._default_task_type
    
    @staticmethod
    def get_supported_tasks() -> Dict[str, Dict]:
        """
        Get all supported task types and their configurations
        
        Returns:
            Dict mapping task types to their configurations
        """
        return config_manager.task_pool["task_types"]
    
    @staticmethod
    def get_task_weights(task_type: str) -> Dict[str, float]:
        """
        Get weights for a specific task type
        
        Args:
            task_type: Task type to get weights for
            
        Returns:
            Dict mapping metric names to their weights
            
        Raises:
            ValueError: If task type is not supported
        """
        if task_type not in TaskManager.get_supported_tasks():
            raise ValueError(f"Unsupported task type: {task_type}")
        return config_manager.get_task_weights(task_type)
    
    @staticmethod
    def get_task_metrics(task_type: str) -> List[str]:
        """
        Get list of metrics for a task type
        
        Args:
            task_type: Task type to get metrics for
            
        Returns:
            List of metric names
            
        Raises:
            ValueError: If task type is not supported
        """
        weights = TaskManager.get_task_weights(task_type)
        return list(weights.keys())
    
    @staticmethod
    def validate_task_type(task_type: Optional[str]) -> str:
        """
        Validate and return task type, using default if None
        
        Args:
            task_type: Task type to validate, or None for default
            
        Returns:
            Validated task type
            
        Raises:
            ValueError: If task type is invalid
        """
        if task_type is None:
            return TaskManager._default_task_type
            
        if task_type not in TaskManager.get_supported_tasks():
            raise ValueError(f"Unsupported task type: {task_type}")
            
        return task_type
    
    @staticmethod
    def get_task_config(task_type: str) -> Dict:
        """
        Get full configuration for a task type
        
        Args:
            task_type: Task type to get configuration for
            
        Returns:
            Task configuration dictionary
            
        Raises:
            ValueError: If task type is not supported
        """
        if task_type not in TaskManager.get_supported_tasks():
            raise ValueError(f"Unsupported task type: {task_type}")
        return config_manager.get_task_config(task_type)
