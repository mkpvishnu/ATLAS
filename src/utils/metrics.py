import statistics
import numpy as np
from scipy import stats
import logging
from typing import List, Dict, Tuple

class MetricsCalculator:
    @staticmethod
    def calculate_confidence_and_reliability(evaluations: List[Dict], criteria: Dict) -> Tuple[float, float]:
        logging.info("Calculating confidence and reliability scores")
        metrics = ["coherence", "relevance", "helpfulness", "context_awareness", "consistency"]
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
        
        max_possible_std = max(max(criteria[metric].keys()) for metric in metrics)
        avg_std_dev = statistics.mean(std_devs) if std_devs else 0
        reliability = 1 - (avg_std_dev / float(max_possible_std))
        
        return round(confidence, 2), round(reliability, 2)

    @staticmethod
    def aggregate_scores(evaluations: List[Dict], criteria: Dict) -> Dict:
        logging.info("Aggregating scores with outlier detection")
        aggregated = {}
        metrics = ["coherence", "relevance", "helpfulness", "context_awareness", "consistency"]
        
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
            
            # z- Scores produces too many outliers
            # z_scores = np.abs(stats.zscore(scores))
            # filtered_scores = [
            #     score for score, z in zip(scores, z_scores) 
            #     if z < 2
            # ]
            
            aggregated[metric] = {
                "score": statistics.median(filtered_scores) if filtered_scores else 0,
                "raw_scores": scores,
                "filtered_scores": filtered_scores,
                "variance": statistics.variance(filtered_scores) if len(filtered_scores) > 1 else 0,
                "justifications": justifications[:3],
                "normalized_score": MetricsCalculator.normalize_score(
                    statistics.median(filtered_scores) if filtered_scores else 0,
                    metric,
                    criteria
                )
            }
        
        return aggregated

    @staticmethod
    def normalize_score(score: float, metric: str, criteria: Dict) -> float:
        max_score = max(float(k) for k in criteria[metric].keys())
        return score / max_score
