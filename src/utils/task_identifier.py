import json
import logging
from pathlib import Path
from typing import Optional
from models.cloudverse import CloudverseClient
from config.api_config import APIConfig

class TaskIdentifier:
    def __init__(self):
        # Load the task pool
        base_path = Path(__file__).parent.parent
        with open(base_path / "pool" / "task_pool.json", "r") as f:
            self.task_pool = json.load(f)
        
        # Initialize LLM client for task identification
        config = APIConfig.CLOUDVERSE_CONFIG
        self.llm_client = CloudverseClient(
            token=config["token"],
            model_name="Azure-GPT-4o-mini"  # Always use mini for task identification
        )

    def identify_task_from_prompt(self, prompt: str) -> str:
        """Identify task type by asking LLM to analyze the prompt."""
        try:
            identification_prompt = f"""Analyze the following prompt and identify which type of task it is requesting. The task types are:

{self._format_task_types()}

Respond with ONLY the task type that best matches the prompt.

Prompt to analyze:
{prompt}

Task type:"""

            response = self.llm_client.generate_response(
                prompt=identification_prompt,
                max_tokens=50,
                temperature=0,
                top_p=1
            )
            
            # Clean and validate response
            task_type = response.strip().lower()
            task_type = task_type.replace('task type:', '').strip()
            
            if task_type in self.task_pool["task_types"]:
                logging.info(f"Identified task type from prompt: {task_type}")
                return task_type
            
            logging.warning(f"LLM returned invalid task type: {task_type}")
            return "conversation_evaluation"  # Default fallback
            
        except Exception as e:
            logging.error(f"Error identifying task type: {str(e)}")
            return "conversation_evaluation"  # Default fallback

    def _format_task_types(self) -> str:
        """Format available task types with their descriptions."""
        task_types = []
        for task_type, config in self.task_pool["task_types"].items():
            description = config.get("description", "No description available")
            task_types.append(f"- {task_type}: {description}")
        return "\n".join(task_types)

# Singleton instance
task_identifier = TaskIdentifier()
