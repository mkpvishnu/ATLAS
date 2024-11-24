from datetime import datetime
import logging
from typing import Dict, Optional, List

from .base_evaluator import BaseEvaluator
from .prompt_generator import PromptGenerator
from .task_manager import TaskManager
from utils.metrics import MetricsCalculator
from utils.llm_parser import LLMResponseParser
from utils.task_identifier import task_identifier
from models.llm_manager import llm_manager

class Evaluator(BaseEvaluator):
    """Base evaluator class"""
    
    def __init__(
        self,
        task_type: Optional[str] = None,
        num_evaluations: int = 1,
        include_justification: bool = True,
        vendor: str = "cloudverse",
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Initialize evaluator
        
        Args:
            task_type: Type of task to evaluate. If None, will use default
            num_evaluations: Number of evaluations to perform
            include_justification: Whether to include justifications in output
            vendor: LLM vendor to use (e.g., 'cloudverse', 'openai')
            api_key: API key for LLM vendor
            model_name: Name of model to use. If None, will use default
        """
        self.task_type = TaskManager.validate_task_type(task_type)
        self.num_evaluations = num_evaluations
        self.include_justification = include_justification
        self.vendor = vendor.lower()
        self.api_key = api_key
        self.model_name = model_name
        
        # Initialize components
        self.prompt_generator = PromptGenerator()
        self.llm_parser = LLMResponseParser()
        self.metrics_calculator = MetricsCalculator()
        
        # Get LLM client
        if not api_key:
            raise ValueError("API key is required")
        self.llm_client = llm_manager.get_client(vendor, api_key, model_name)
        
        logging.info(f"Initialized evaluator with {num_evaluations} evaluations for {self.task_type}")
    
    def evaluate(self, content: str) -> Dict:
        """
        Evaluate content
        
        Args:
            content: Content to evaluate
            
        Returns:
            Dict containing evaluation results
        """
        try:
            # Identify task type from prompt if not set
            if not self.task_type:
                self.task_type = task_identifier.identify_task_type(content)
                logging.info(f"Identified task type: {self.task_type}")
            
            all_evaluations = []
            for _ in range(self.num_evaluations):
                # Generate evaluation prompt
                evaluation_prompt = self.prompt_generator.generate_prompt(
                    content,
                    self.task_type,
                    include_justification=self.include_justification
                )
                
                # Get evaluation from LLM
                evaluation = self._get_llm_evaluation(
                    evaluation_prompt,
                    include_justification=self.include_justification
                )
                all_evaluations.append(evaluation)
            
            # Aggregate results
            result = self.metrics_calculator.aggregate_scores(
                all_evaluations,
                self.task_type
            )
            
            # Add metadata
            result["metadata"] = {
                "task_type": self.task_type,
                "num_evaluations": self.num_evaluations,
                "timestamp": datetime.utcnow().isoformat(),
                "model": {
                    "vendor": self.vendor,
                    "name": self.model_name
                }
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error in evaluation: {str(e)}")
            raise

    def _get_llm_evaluation(self, prompt: str, include_justification: bool = True) -> Dict:
        """Get evaluation from LLM and parse the response"""
        try:
            # Get default params for vendor
            params = llm_manager.get_default_params(self.vendor)
            
            # Generate response
            response = self.llm_client.generate_response(prompt, **params)
            
            # Parse response
            return self.llm_parser.parse_evaluation_response(
                response,
                self.task_type,
                include_justification
            )
            
        except Exception as e:
            logging.error(f"Error getting LLM evaluation: {str(e)}")
            raise
