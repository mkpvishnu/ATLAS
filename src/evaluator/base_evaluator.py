from abc import ABC, abstractmethod
import json
import logging
import os

class BaseEvaluator(ABC):
    def __init__(self, task_type: str, num_evaluations: int = 5):
        self.task_type = task_type
        self.num_evaluations = num_evaluations
        self.evaluation_criteria = self._load_evaluation_criteria()
        logging.info(f"Initialized {task_type} evaluator with {num_evaluations} evaluations")

    def _load_evaluation_criteria(self) -> dict:
        try:
            config_path = os.path.join(os.path.dirname(__file__), '../config/evaluation_criteria.json')
            with open(config_path, 'r') as f:
                criteria = json.load(f)
                logging.info(f"Loaded evaluation criteria for {self.task_type}")
                return criteria[self.task_type]
        except Exception as e:
            logging.error(f"Error loading evaluation criteria: {str(e)}")
            raise

    @abstractmethod
    def evaluate(self, content: str) -> dict:
        pass
