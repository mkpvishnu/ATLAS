from abc import ABC, abstractmethod
import logging

class BaseEvaluator(ABC):
    def __init__(self, task_type: str = None, num_evaluations: int = 5):
        self.task_type = task_type
        self.num_evaluations = num_evaluations
        logging.info(f"Initialized evaluator with {num_evaluations} evaluations" + 
                    (f" for {task_type}" if task_type else ""))

    @abstractmethod
    def evaluate(self, content: str) -> dict:
        pass
