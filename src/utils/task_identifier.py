import logging
from typing import Optional
from models.llm_manager import llm_manager
from evaluator.task_manager import TaskManager

class TaskIdentifier:
    """Identifies task type from content using LLM"""
    
    def __init__(self, vendor: str = "cloudverse", api_key: Optional[str] = None):
        """
        Initialize task identifier
        
        Args:
            vendor: LLM vendor to use
            api_key: API key for vendor
        """
        if not api_key:
            raise ValueError("API key is required for task identification")
            
        self.llm_client = llm_manager.get_client(vendor, api_key)
        self.supported_tasks = TaskManager.get_supported_tasks()
        
    def identify_task_type(self, content: str, custom_prompt: Optional[str] = None) -> str:
        """
        Identify task type from content
        
        Args:
            content: Content to analyze
            custom_prompt: Optional custom prompt for task identification
            
        Returns:
            Identified task type
            
        Raises:
            ValueError: If task type cannot be identified
        """
        try:
            # Get task types for prompt
            task_types = list(self.supported_tasks.keys())
            task_descriptions = {
                task: config.get("description", "No description available")
                for task, config in self.supported_tasks.items()
            }
            
            # Generate identification prompt
            if custom_prompt:
                prompt = custom_prompt
            else:
                prompt = self._generate_identification_prompt(content, task_types, task_descriptions)
            
            # Get response from LLM
            params = llm_manager.get_default_params("cloudverse")
            response = self.llm_client.generate_response(prompt, **params)
            
            # Parse response
            task_type = self._parse_task_type(response, task_types)
            if not task_type:
                raise ValueError("Could not identify task type from LLM response")
                
            return task_type
            
        except Exception as e:
            logging.error(f"Error identifying task type: {str(e)}")
            # Fall back to default task type
            logging.info("Falling back to default task type")
            return TaskManager.get_default_task_type()
            
    def _generate_identification_prompt(self, content: str, task_types: list, task_descriptions: dict) -> str:
        """Generate prompt for task identification"""
        task_options = "\n".join([
            f"- {task}: {task_descriptions[task]}"
            for task in task_types
        ])
        
        return f"""Please analyze the following content and identify the most appropriate task type for evaluation.
Available task types:
{task_options}

Content to analyze:
{content}

Please respond with ONLY the task type name that best matches the content. For example: conversation_evaluation
Do not include any other text or explanation in your response."""
            
    def _parse_task_type(self, response: str, valid_tasks: list) -> Optional[str]:
        """
        Parse task type from LLM response
        
        Args:
            response: LLM response text
            valid_tasks: List of valid task types
            
        Returns:
            Task type if found, None otherwise
        """
        # Clean and normalize response
        task_type = response.strip().lower()
        
        # Check if response matches any valid task
        for valid_task in valid_tasks:
            if valid_task.lower() in task_type:
                return valid_task
                
        return None
        
# Singleton instance
task_identifier = TaskIdentifier(vendor="cloudverse", api_key="your_api_key")
