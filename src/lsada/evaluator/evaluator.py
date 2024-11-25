from datetime import datetime
import logging
from typing import Dict, Optional, List

from .base_evaluator import BaseEvaluator
from .prompt_generator import PromptGenerator
from .task_manager import TaskManager
from lsada.utils.metrics import MetricsCalculator
from lsada.utils.llm_parser import LLMResponseParser
from lsada.models.llm_manager import BaseLLMClient

class Evaluator(BaseEvaluator):
    """Base evaluator class"""
    
    def __init__(
        self,
        task_type: Optional[str] = None,
        num_evaluations: int = 1,
        include_justification: bool = True
    ):
        """
        Initialize evaluator
        
        Args:
            task_type: Type of task to evaluate. If None, will use default
            num_evaluations: Number of evaluations to perform
            include_justification: Whether to include justifications in output
        """
        self.task_type = TaskManager.validate_task_type(task_type)
        self.num_evaluations = num_evaluations
        self.include_justification = include_justification
        
        # Initialize components
        self.prompt_generator = PromptGenerator()
        self.llm_parser = LLMResponseParser()
        self.metrics_calculator = MetricsCalculator()
        
        logging.info(f"Initialized evaluator with {num_evaluations} evaluations for {self.task_type}")
    
    def evaluate(self, content: str, llm_client: BaseLLMClient) -> Dict:
        """
        Evaluate content using provided LLM client
        
        Args:
            content: Content to evaluate
            llm_client: Initialized LLM client to use for evaluation
            
        Returns:
            Dict containing evaluation results
        """
        try:
            # Identify task type from prompt if not set
            if not self.task_type:
                self.task_type = TaskManager.identify_task_type(content)
                logging.info(f"Identified task type: {self.task_type}")
            
            all_evaluations = []
            for _ in range(self.num_evaluations):
                # Generate evaluation prompt
                evaluation_prompt = self.prompt_generator.generate_prompt(
                    self.task_type,
                    content,
                    include_justification=self.include_justification
                )
                
                # Get evaluation from LLM
                evaluation = self._get_llm_evaluation(
                    llm_client,
                    evaluation_prompt,
                    include_justification=self.include_justification
                )
                all_evaluations.append(evaluation)
            
            # Aggregate results
            result = self.metrics_calculator.aggregate_scores(
                all_evaluations,
                self.task_type
            )
            if self.include_justification:
                metrics = TaskManager.get_metrics_for_task(self.task_type)
                for metric in metrics:
                    result["Scores"][metric]["justifications"] = [evaluation["justifications"][metric] for evaluation in all_evaluations]
            
            # Add metadata
            result["metadata"] = {
                "task_type": self.task_type,
                "num_evaluations": self.num_evaluations,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error in evaluation: {str(e)}")
            raise

    def _get_llm_evaluation(self, llm_client: BaseLLMClient, prompt: str, include_justification: bool = True) -> Dict:
        """Get evaluation from LLM and parse the response"""
        try:
            # Generate response
            response = llm_client.generate_response(prompt)
            
            # Parse response
            return self.llm_parser.parse_evaluation_response(
                response,
                self.task_type,
                include_justification
            )
            
        except Exception as e:
            logging.error(f"Error getting LLM evaluation: {str(e)}")
            raise
