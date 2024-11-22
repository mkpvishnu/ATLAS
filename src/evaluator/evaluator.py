from datetime import datetime
import logging
from typing import Dict

from .base_evaluator import BaseEvaluator
from .prompt_generator import PromptGenerator
from utils.metrics import MetricsCalculator
from utils.llm_parser import LLMResponseParser
from models.cloudverse import CloudverseClient
from config.evaluation_config import EvaluationConfig
from config.api_config import APIConfig

class Evaluator(BaseEvaluator):
    def __init__(self, task_type: str, num_evaluations: int = 5):
        """
        Initialize evaluator for any task type
        
        Args:
            task_type: Type of evaluation task (e.g., "conversation_evaluation", "code_quality_evaluation")
            num_evaluations: Number of evaluations to perform
        """
        super().__init__(task_type, num_evaluations)
        self.weights = EvaluationConfig.get_weights(self.task_type)
        self.metrics = list(self.weights.keys())
        
        # Initialize LLM client with config
        config = APIConfig.CLOUDVERSE_CONFIG
        self.llm_client = CloudverseClient(
            token=config["token"],
            model_name=config["model_name"]
        )

        logging.info(f"Initialized evaluator for {task_type} with {num_evaluations} evaluations")

    def evaluate(self, content: str) -> Dict:
        """
        Evaluate content based on task type
        
        Args:
            content: Content to evaluate (conversation text, code, etc.)
        
        Returns:
            Dict containing evaluation results
        """
        all_evaluations = []
        
        for i in range(self.num_evaluations):
            logging.info(f"Performing evaluation {i+1}/{self.num_evaluations}")
            prompt = PromptGenerator.generate_prompt(
                self.task_type,
                content, 
                self.evaluation_criteria
            )
            evaluation = self._get_llm_evaluation(prompt)
            all_evaluations.append(evaluation)
        
        aggregated_scores = MetricsCalculator.aggregate_scores(
            all_evaluations, 
            self.evaluation_criteria
        )
        confidence, reliability = MetricsCalculator.calculate_confidence_and_reliability(
            all_evaluations,
            self.evaluation_criteria
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
                "weights": self.weights,
                "task_type": self.task_type
            }
        }

    def _calculate_final_score(self, aggregated_scores: Dict) -> float:
        weighted_sum = 0
        for metric, weight in self.weights.items():
            weighted_sum += aggregated_scores[metric]["normalized_score"] * weight
        return round(weighted_sum, 2)

    def _get_llm_evaluation(self, prompt: str) -> Dict:
        """Get evaluation from LLM and parse the response"""
        try:
            config = APIConfig.CLOUDVERSE_CONFIG["default_params"]
            response = self.llm_client.generate_response(
                prompt=prompt,
                **config
            )
            return LLMResponseParser.parse_evaluation_response(response, self.metrics)
            
        except Exception as e:
            logging.error(f"Error getting LLM evaluation: {str(e)}")
            raise
