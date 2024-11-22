from typing import Dict

class EvaluationConfig:
    WEIGHTS = {
        "conversation_evaluation": {
            "coherence": 0.25,
            "relevance": 0.25,
            "helpfulness": 0.25,
            "context_awareness": 0.15,
            "consistency": 0.10
        },
        "code_quality_evaluation": {
            "readability": 0.25,
            "maintainability": 0.25,
            "efficiency": 0.20,
            "best_practices": 0.15,
            "error_handling": 0.15
        }
    }

    @classmethod
    def get_weights(cls, task_type: str) -> Dict[str, float]:
        if task_type not in cls.WEIGHTS:
            raise ValueError(f"No weights defined for task type: {task_type}")
        return cls.WEIGHTS[task_type]
