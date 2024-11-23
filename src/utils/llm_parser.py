import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from config.config_manager import config_manager

class LLMResponseParser:
    """Parses LLM responses for evaluation tasks"""

    def parse_evaluation_response(self, response: str, task_type: str) -> Dict:
        """
        Parse LLM evaluation response into structured format
        
        Args:
            response: Raw LLM response text
            task_type: Type of evaluation task
            
        Returns:
            Dict containing parsed scores and justifications
        """
        try:
            task_config = config_manager.get_task_config(task_type)
            metrics = task_config["weightages"].keys()
            
            result = {}
            total_weighted_score = 0
            total_weight = 0
            
            for metric in metrics:
                metric_config = config_manager.get_metrics_config(metric)
                score_range = metric_config.get("score_range", {"min": 0, "max": 10})
                weight = task_config["weightages"][metric]
                
                score, justification = self._extract_metric_data(response, metric)
                
                # Validate and normalize score
                score = self._validate_score(score, score_range["min"], score_range["max"])
                normalized_score = self._normalize_score(score, score_range["min"], score_range["max"])
                
                result[f"{metric}_score"] = score
                result[f"{metric}_normalized_score"] = normalized_score
                result[f"{metric}_justification"] = justification
                
                total_weighted_score += normalized_score * weight
                total_weight += weight
            
            # Add total weighted score
            if total_weight > 0:
                result["total_weighted_score"] = total_weighted_score / total_weight
            else:
                result["total_weighted_score"] = 0
                
            return result
            
        except Exception as e:
            logging.error(f"Error parsing evaluation response: {str(e)}")
            raise ValueError(f"Failed to parse evaluation response: {str(e)}")
            
    def _extract_metric_data(self, response: str, metric: str) -> Tuple[float, str]:
        """Extract score and justification for a metric from response"""
        try:
            # Look for score pattern: METRIC_SCORE: number
            score_pattern = rf"{metric.upper()}_SCORE:\s*(\d+(?:\.\d+)?)"
            score_match = re.search(score_pattern, response)
            
            # Look for justification pattern: METRIC_JUSTIFICATION: text
            justification_pattern = rf"{metric.upper()}_JUSTIFICATION:\s*(.+?)(?=\w+_(?:SCORE|JUSTIFICATION):|$)"
            justification_match = re.search(justification_pattern, response, re.DOTALL)
            
            if not score_match:
                raise ValueError(f"Could not find score for metric {metric}")
                
            score = float(score_match.group(1))
            justification = justification_match.group(1).strip() if justification_match else "No justification provided"
            
            return score, justification
            
        except Exception as e:
            logging.error(f"Error extracting metric data: {str(e)}")
            return 0.0, f"Error extracting data: {str(e)}"
            
    def _validate_score(self, score: float, min_score: float, max_score: float) -> float:
        """Validate score is within allowed range"""
        if score < min_score:
            logging.warning(f"Score {score} below minimum {min_score}, using minimum")
            return min_score
        if score > max_score:
            logging.warning(f"Score {score} above maximum {max_score}, using maximum")
            return max_score
        return score
        
    def _normalize_score(self, score: float, min_score: float, max_score: float) -> float:
        """Normalize score to 0-1 range"""
        if max_score == min_score:
            return 1.0 if score >= max_score else 0.0
        return (score - min_score) / (max_score - min_score)
