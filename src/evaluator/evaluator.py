from datetime import datetime
import logging
from typing import Dict, Optional

from .base_evaluator import BaseEvaluator
from .prompt_generator import PromptGenerator
from utils.metrics import MetricsCalculator
from utils.llm_parser import LLMResponseParser
from utils.task_identifier import task_identifier
from models.cloudverse import CloudverseClient
from config.api_config import APIConfig
from config.config_manager import config_manager

class Evaluator(BaseEvaluator):
    def __init__(self, task_type: Optional[str] = None, num_evaluations: int = 5, model_name: Optional[str] = None):
        """
        Initialize evaluator for any task type
        
        Args:
            task_type: Type of evaluation task (optional)
            num_evaluations: Number of evaluations to perform
            model_name: Override default model name
        """
        super().__init__(task_type, num_evaluations)
        if task_type:
            self.weights = config_manager.get_task_weights(task_type)
            self.metrics = list(self.weights.keys())
        
        # Initialize components
        self.prompt_generator = PromptGenerator()
        self.metrics_calculator = MetricsCalculator()
        self.llm_parser = LLMResponseParser()
        
        # Initialize LLM client with config
        config = APIConfig.CLOUDVERSE_CONFIG.copy()
        if model_name:
            config["model_name"] = model_name
        self.llm_client = CloudverseClient(
            token=config["token"],
            model_name=config["model_name"]
        )

        logging.info(f"Initialized evaluator with {num_evaluations} evaluations" + 
                    (f" for {task_type}" if task_type else ""))

    def evaluate(self, content: str, prompt: Optional[str] = None) -> Dict:
        """
        Evaluate content based on task type
        
        Args:
            content: Content to evaluate (conversation text, code, etc.)
            prompt: Original prompt that generated the content (optional)
        
        Returns:
            Dict containing evaluation results
        """
        # If no task type was provided during initialization, identify it from prompt
        if not self.task_type and prompt:
            self.task_type = task_identifier.identify_task_from_prompt(prompt)
            logging.info(f"Identified task type from prompt: {self.task_type}")
            # Update weights based on identified task type
            self.weights = config_manager.get_task_weights(self.task_type)
            self.metrics = list(self.weights.keys())
        elif not self.task_type:
            # Default to conversation evaluation if no prompt and no task type
            self.task_type = "conversation_evaluation"
            logging.info("No prompt provided, defaulting to conversation evaluation")
            self.weights = config_manager.get_task_weights(self.task_type)
            self.metrics = list(self.weights.keys())
        
        all_evaluations = []
        
        for i in range(self.num_evaluations):
            logging.info(f"Performing evaluation {i+1}/{self.num_evaluations}")
            evaluation_prompt = self.prompt_generator.generate_prompt(
                self.task_type,
                content
            )
            print(evaluation_prompt)
            evaluation = self._get_llm_evaluation(evaluation_prompt)
            print(evaluation)
            all_evaluations.append(evaluation)
        
        aggregated_scores = self.metrics_calculator.aggregate_scores(
            all_evaluations, 
            self.task_type
        )
        confidence, reliability = self.metrics_calculator.calculate_confidence_and_reliability(
            all_evaluations,
            self.task_type
        )
        final_score = self._calculate_final_score(aggregated_scores)
        
        return {
            "final_score": final_score,
            "confidence": confidence,
            "reliability": reliability,
            "metric_scores": aggregated_scores,
            "evaluation_metadata": {
                "num_evaluations": self.num_evaluations,
                "timestamp": datetime.now().isoformat(),
                "weightages": self.weights,
                "task_type": self.task_type,
                "model_name": self.llm_client.model_name
            }
        }

    def _calculate_final_score(self, aggregated_scores: Dict) -> float:
        return round(aggregated_scores.get("total_weighted_score", 0), 2)

    def _get_llm_evaluation(self, prompt: str) -> Dict:
        """Get evaluation from LLM and parse the response"""
        try:
            config = APIConfig.CLOUDVERSE_CONFIG["default_params"]
            response = self.llm_client.generate_response(
                prompt=prompt,
                **config
            )
            #Print full response including headers
            print(f"Full response: {response}")
            
            return self.llm_parser.parse_evaluation_response(response, self.task_type)
            
        except Exception as e:
            logging.error(f"Error getting LLM evaluation: {str(e)}")
            raise
