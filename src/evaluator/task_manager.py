from typing import Dict, List, Optional
import logging
from config.config_manager import config_manager
from models.llm_manager import LLMManager

class TaskManager:
    """Manages task types and their configurations"""
    
    _default_task_type = "conversation_evaluation"  # Class-level default task type
    _llm_client = None  # LLM client for task identification
    
    @classmethod
    def initialize_llm_client(cls, vendor: str = "cloudverse", api_key: Optional[str] = None, **kwargs):
        """Initialize LLM client for task identification"""
        if not api_key:
            raise ValueError("API key is required for task identification")
        cls._llm_client = LLMManager.initialize_client(vendor, api_key, **kwargs)
    
    @staticmethod
    def get_supported_tasks() -> Dict[str, Dict]:
        """Get all supported task types and their configurations"""
        return config_manager.task_pool["task_types"]
    
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
    
    @classmethod
    def identify_task_type(cls, content: str, custom_prompt: Optional[str] = None) -> str:
        """
        Identify task type from content using LLM
        
        Args:
            content: Content to analyze
            custom_prompt: Optional custom prompt for task identification
            
        Returns:
            Identified task type
            
        Raises:
            ValueError: If task type cannot be identified or LLM client not initialized
        """
        if not cls._llm_client:
            raise ValueError("LLM client not initialized. Call initialize_llm_client first.")
            
        try:
            # Get task types for prompt
            supported_tasks = cls.get_supported_tasks()
            task_types = list(supported_tasks.keys())
            task_descriptions = {
                task: config.get("description", "No description available")
                for task, config in supported_tasks.items()
            }
            
            # Generate identification prompt
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = cls._generate_identification_prompt(content, task_types, task_descriptions)
            
            # Get response from LLM
            response = cls._llm_client.generate_response(prompt)
            
            # Parse response to get task type
            identified_task = cls._parse_task_type(response, task_types)
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
