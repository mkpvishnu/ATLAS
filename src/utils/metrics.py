import statistics
import numpy as np
from scipy import stats
import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class MetricsCalculator:
    def __init__(self):
        # Load the metrics and task pools
        base_path = Path(__file__).parent.parent
        with open(base_path / "pool" / "metrics_pool.json", "r") as f:
            self.metrics_pool = json.load(f)
        with open(base_path / "pool" / "task_pool.json", "r") as f:
            self.task_pool = json.load(f)

    def get_metrics_for_task(self, task_type: str) -> List[str]:
        """Get the list of metrics for a given task type."""
        if task_type not in self.task_pool["task_types"]:
            raise ValueError(f"Task type {task_type} not found in task pool")
        return list(self.task_pool["task_types"][task_type]["weightages"].keys())

    def get_max_score(self, metric_name: str) -> float:
        """Get the maximum possible score for a given metric."""
        for metric_group in self.metrics_pool.values():
            if metric_name in metric_group:
                return max(float(score) for score in metric_group[metric_name]["scoring_criteria"].keys())
        raise ValueError(f"Metric {metric_name} not found in metrics pool")

    def calculate_confidence_and_reliability(self, evaluations: List[Dict], task_type: str) -> Tuple[float, float]:
        """Calculate confidence and reliability scores for evaluations."""
        logging.info("Calculating confidence and reliability scores")
        metrics = self.get_metrics_for_task(task_type)
        variances = []
        std_devs = []
        
        for metric in metrics:
            score_key = f"{metric}_score"
            scores = [eval.get(score_key, 0) for eval in evaluations]
            
            if len(scores) > 1:
                variance = statistics.variance(scores)
                variances.append(variance)
                std_dev = statistics.stdev(scores)
                std_devs.append(std_dev)
        
        avg_variance = statistics.mean(variances) if variances else 0
        confidence = 1 / (1 + avg_variance)
        
        max_possible_std = max(self.get_max_score(metric) for metric in metrics)
        avg_std_dev = statistics.mean(std_devs) if std_devs else 0
        reliability = 1 - (avg_std_dev / float(max_possible_std))
        
        return round(confidence, 2), round(reliability, 2)

    def aggregate_scores(self, evaluations: List[Dict], task_type: str) -> Dict:
        """Aggregate scores with outlier detection."""
        logging.info("Aggregating scores with outlier detection")
        aggregated = {}
        metrics = self.get_metrics_for_task(task_type)
        weightages = self.task_pool["task_types"][task_type]["weightages"]
        
        for metric in metrics:
            score_key = f"{metric}_score"
            justification_key = f"{metric}_justification"
            
            scores = [eval.get(score_key, 0) for eval in evaluations]
            justifications = [eval.get(justification_key, "") for eval in evaluations]
            
            # Remove outliers using IQR method
            q1 = np.percentile(scores, 25)
            q3 = np.percentile(scores, 75)
            iqr = q3 - q1
            filtered_scores = [
                s for s in scores 
                if (q1 - 1.5 * iqr) <= s <= (q3 + 1.5 * iqr)
            ]
            
            median_score = statistics.median(filtered_scores) if filtered_scores else 0
            normalized_score = self.normalize_score(median_score, metric)
            weighted_score = normalized_score * weightages[metric]
            
            aggregated[metric] = {
                "score": median_score,
                "raw_scores": scores,
                "filtered_scores": filtered_scores,
                "variance": statistics.variance(filtered_scores) if len(filtered_scores) > 1 else 0,
                "justifications": justifications[:3],
                "normalized_score": normalized_score,
                "weighted_score": weighted_score,
                "weight": weightages[metric]
            }
        
        # Add total weighted score
        total_weighted_score = sum(metric_data["weighted_score"] for metric_data in aggregated.values())
        aggregated["total_weighted_score"] = total_weighted_score
        
        return aggregated

    def normalize_score(self, score: float, metric: str) -> float:
        """Normalize a score based on the maximum possible score for the metric."""
        max_score = self.get_max_score(metric)
        return score / max_score
