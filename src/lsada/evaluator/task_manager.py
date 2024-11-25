from typing import Dict, List, Optional
import logging
from lsada.config.config_manager import config_manager
from lsada.models.llm_manager import LLMManager

class TaskManager:
    """Manages task types and their configurations"""
    
    _default_task_type = "conversation_evaluation"  # Class-level default task type
    
    @classmethod
    def initialize_llm_client(cls, vendor: str = "cloudverse", api_key: Optional[str] = None, **kwargs):
        """Initialize LLM client for task identification"""
        if not api_key:
            raise ValueError("API key is required for task identification")
        return LLMManager.initialize_client(vendor, api_key, **kwargs)
    
    @staticmethod
    def get_supported_tasks() -> Dict[str, Dict]:
        """Get all supported task types and their configurations"""
        return config_manager.task_pool["task_types"]

    @staticmethod
    def get_supported_tasks_with_descriptions() -> Dict[str, str]:
        """
        Get all supported task types with their descriptions
        
        Returns:
            Dictionary mapping task types to their descriptions
        """
        supported_tasks = TaskManager.get_supported_tasks()
        return {
            task_type: config.get("description", "No description available")
            for task_type, config in supported_tasks.items()
        }

    @staticmethod
    def get_metrics_for_task(task_type: str) -> List[str]:
        """Get list of metrics for a task type"""
        if task_type not in TaskManager.get_supported_tasks():
            raise ValueError(f"Unsupported task type: {task_type}")
        return list(config_manager.get_task_config(task_type)["weightages"].keys())
    
    @staticmethod
    def get_weightages_for_task(task_type: str) -> Dict[str, float]:
        """Get weightages for metrics of a task type"""
        if task_type not in TaskManager.get_supported_tasks():
            raise ValueError(f"Unsupported task type: {task_type}")
        return config_manager.get_task_config(task_type)["weightages"]

    @staticmethod
    def get_details_for_task(task_type: str) -> Dict[str, float]:
        """Get details for a task type"""
        if task_type not in TaskManager.get_supported_tasks():
            raise ValueError(f"Unsupported task type: {task_type}")
        return config_manager.get_task_config(task_type)
    
    @staticmethod
    def identify_task_type(content: str, llm_client) -> str:
        """
        Identify task type from content using LLM
        
        Args:
            content: Content to analyze
            llm_client: LLM client instance to use for task identification
            custom_prompt: Optional custom prompt for task identification
            
        Returns:
            Identified task type
            
        Raises:
            ValueError: If task type cannot be identified
        """
        try:
            # Get task types for prompt
            supported_tasks = TaskManager.get_supported_tasks()
            task_types = list(supported_tasks.keys())
            task_descriptions = {
                task: config.get("description", "No description available")
                for task, config in supported_tasks.items()
            }
            
            prompt = TaskManager._generate_identification_prompt(content, task_types, task_descriptions)
            
            # Get response from LLM
            response = llm_client.generate_response(prompt)
            
            # Parse response to get task type
            identified_task = TaskManager._parse_task_type(response, task_types)
            if not identified_task:
                raise ValueError("Could not identify task type from LLM response")
                
            logging.info(f"Identified task type: {identified_task}")
            return identified_task
            
        except Exception as e:
            logging.error(f"Error identifying task type: {str(e)}")
            raise
    
    @staticmethod
    def _generate_identification_prompt(content: str, task_types: List[str], task_descriptions: Dict[str, str]) -> str:
        """Generate prompt for task identification"""
        prompt = "Please identify the most appropriate task type for the following content.\n\n"
        prompt += "Available task types:\n"
        for task in task_types:
            prompt += f"- {task}: {task_descriptions[task]}\n"
        
        prompt += "\nContent to analyze:\n"
        prompt += f"{content}\n\n"
        prompt += "Please respond with ONLY the task type that best matches the content. "
        prompt += "Choose from the available task types listed above."
        
        return prompt
    
    @staticmethod
    def _parse_task_type(response: str, valid_tasks: List[str]) -> Optional[str]:
        """Parse task type from LLM response"""
        # Clean response
        response = response.strip().lower()
        
        # Check each valid task
        for task in valid_tasks:
            if task.lower() in response:
                return task
                
        return None
    
    @staticmethod
    def validate_task_type(task_type: Optional[str]) -> str:
        """Validate and return task type, using default if None"""
        if task_type is None:
            return TaskManager._default_task_type
            
        if task_type not in TaskManager.get_supported_tasks():
            raise ValueError(f"Unsupported task type: {task_type}")
            
        return task_type
