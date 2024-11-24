from typing import List, Dict, Tuple, Any
import statistics
import numpy as np
import logging
from lsada.config.config_manager import config_manager
from lsada.evaluator.task_manager import TaskManager

class MetricsCalculator:
    """Class for calculating metrics and scores"""
    
    def __init__(self):
        """Initialize MetricsCalculator"""
        self.task_manager = TaskManager()
        self.metrics_pool = config_manager.metrics_pool

    def get_max_score(self, metric_name: str) -> float:
        """Get the maximum possible score for a given metric."""
        if metric_name in self.metrics_pool:
            return max(float(score) for score in self.metrics_pool[metric_name]["scoring_criteria"].keys())
        raise ValueError(f"Metric {metric_name} not found in metrics pool")

    def calculate_confidence_and_reliability(self, evaluations: List[Dict], task_type: str) -> Tuple[float, float]:
        """Calculate confidence and reliability scores for evaluations."""
        logging.info("Calculating confidence and reliability scores")
        
        try:
            metrics = self.task_manager.get_metrics_for_task(task_type)
            
            # Calculate standard deviation for each metric
            std_devs = {}
            for metric in metrics:
                scores = [eval.get("raw_scores", {}).get(metric, 0) for eval in evaluations]
                std_devs[metric] = np.std(scores) if scores else 0
                
            # Calculate confidence score (inverse of average standard deviation)
            avg_std = sum(std_devs.values()) / len(std_devs) if std_devs else 0
            max_score = max(self.get_max_score(metric) for metric in metrics)
            confidence = 1 - (avg_std / max_score) if max_score > 0 else 0
            
            # Calculate reliability score (based on number of evaluations)
            max_reliability = 0.95  # Maximum achievable reliability
            reliability = min(len(evaluations) / 5, 1) * max_reliability
            
            return confidence, reliability
            
        except Exception as e:
            logging.error(f"Error calculating confidence and reliability: {str(e)}")
            return 0.0, 0.0

    def normalize_score(self, score: float, metric: str) -> float:
        """Normalize a score based on the metric's maximum score"""
        try:
            max_score = self.get_max_score(metric)
            return score / max_score if max_score > 0 else 0
        except Exception as e:
            logging.error(f"Error normalizing score: {str(e)}")
            return 0.0
            
    def aggregate_scores(self, evaluations: List[Dict], task_type: str) -> Dict[str, Any]:
        """Aggregate scores from multiple evaluations."""
        try:
            logging.info("Aggregating scores with outlier detection")
            aggregated = {"Scores": {}}
            metrics = self.task_manager.get_metrics_for_task(task_type)
            weightages = self.task_manager.get_weightages_for_task(task_type)
            
            for metric in metrics:
                scores = [eval.get("raw_scores", 0).get(metric) for eval in evaluations]

                # Remove outliers using IQR method
                q1 = np.percentile(scores, 25)
                q3 = np.percentile(scores, 75)
                iqr = q3 - q1
                lower_bound = q1 - 2.5 * iqr
                upper_bound = q3 + 2.5 * iqr
                
                filtered_scores = [s for s in scores if lower_bound <= s <= upper_bound]
                
                median_score = statistics.median(filtered_scores) if filtered_scores else 0
                normalized_score = self.normalize_score(median_score, metric)
                weighted_score = normalized_score * weightages[metric]
                
                aggregated["Scores"][metric] = {
                    "score": median_score,
                    "raw_scores": scores,
                    "filtered_scores": filtered_scores,
                    "variance": statistics.variance(filtered_scores) if len(filtered_scores) > 1 else 0,
                    "normalized_score": normalized_score,
                    "weighted_score": weighted_score,
                    "weight": weightages[metric]
                }
            
            # Calculate total weighted score
            total_weighted_score = 0
            for metric, metric_data in aggregated["Scores"].items():
                total_weighted_score += metric_data["weighted_score"]
            
            aggregated["total_weighted_score"] = round(total_weighted_score, 2)
            
            return aggregated
        except Exception as e:
            logging.error(f"Error in Aggregation: {str(e)}")
            raise
