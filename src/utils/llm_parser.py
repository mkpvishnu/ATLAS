import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from config.config_manager import config_manager

class LLMResponseParser:
    """Parses LLM responses for evaluation tasks"""

    def parse_evaluation_response(self, response: str, task_type: str, include_justification: bool = True) -> Dict:
        """
        Parse LLM evaluation response into structured format
        
        Args:
            response: Raw LLM response text
            task_type: Type of evaluation task
            include_justification: Whether to include justifications in the output
            
        Returns:
            Dict containing parsed scores and justifications
        """
        try:
            task_config = config_manager.get_task_config(task_type)
            result = {
                "raw_scores": {},
                "normalized_scores": {},
                "validation_issues": []
            }
            
            if include_justification:
                result["justifications"] = {}
            
            total_weighted_score = 0
            total_weight = 0
            
            # Process each metric
            for metric, weight in task_config["weightages"].items():
                try:
                    metric_config = config_manager.get_metrics_config(metric)
                    score_range = metric_config.get("score_range", {"min": 0, "max": 10})
                    
                    # Extract score and justification
                    if include_justification:
                        score, justification = self._extract_metric_data(response, metric)
                        result["justifications"][metric] = self._validate_justification(
                            justification, metric, result["validation_issues"]
                        )
                    else:
                        score = self._extract_score(response, metric)
                    
                    # Validate and normalize score
                    score = self._validate_score(score, score_range["min"], score_range["max"])
                    normalized_score = self._normalize_score(score, score_range["min"], score_range["max"])
                    
                    result["raw_scores"][metric] = score
                    result["normalized_scores"][metric] = normalized_score
                    print(f"Metric: {metric}, Score: {score}, Normalized Score: {normalized_score}")
                    
                    total_weighted_score += normalized_score * weight
                    total_weight += weight
                    print(f"Total Weighted Score: {total_weighted_score}, Total Weight: {total_weight}")
                
                except Exception as e:
                    logging.error(f"Error processing metric {metric}: {str(e)}")
                    result["validation_issues"].append(f"Error processing metric {metric}: {str(e)}")
            
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
            print(score)
            justification = justification_match.group(1).strip() if justification_match else "No justification provided"
            
            return score, justification
            
        except Exception as e:
            logging.error(f"Error extracting metric data: {str(e)}")
            return 0.0, f"Error extracting data: {str(e)}"
            
    def _extract_score(self, response: str, metric: str) -> float:
        """Extract score for a metric from response"""
        try:
            # Look for score pattern: METRIC_SCORE: number
            score_pattern = rf"{metric.upper()}_SCORE:\s*(\d+(?:\.\d+)?)"
            score_match = re.search(score_pattern, response)
            print(score_match)
            
            if not score_match:
                raise ValueError(f"Could not find score for metric {metric}")
                
            score = float(score_match.group(1))
            
            return score
            
        except Exception as e:
            logging.error(f"Error extracting score: {str(e)}")
            return 0.0
            
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
        
    def _validate_justification(self, justification: str, metric: str, validation_issues: list) -> str:
        """Validate justification for a metric"""
        try:
            # Add validation logic here if needed
            return justification
            
        except Exception as e:
            logging.error(f"Error validating justification for metric {metric}: {str(e)}")
            validation_issues.append(f"Error validating justification for metric {metric}: {str(e)}")
            return "No justification provided"
