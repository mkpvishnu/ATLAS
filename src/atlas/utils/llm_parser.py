import json
import logging
import re
from typing import Dict, Optional, Tuple, List
from ..config.models import EvaluationConfig
from ..config.config_manager import config_manager

class LLMResponseParser:
    """Parses LLM responses for evaluation tasks"""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
    
    def parse_evaluation_response(self, response: str) -> Dict:
        """Parse LLM evaluation response into structured format"""
        try:
            task_type = self.config.task_type
            task_config = config_manager.get_task_config(task_type)
            result = {
                "raw_scores": {},
                "normalized_scores": {},
                "validation_issues": []
            }
            
            if self.config.include_justification:
                result["justifications"] = {}
            
            total_weighted_score = 0
            total_weight = 0
            
            # Process each metric
            for metric, weight in task_config["weightages"].items():
                try:
                    metric_config = config_manager.get_metrics_config(metric)
                    score_range = metric_config.get("score_range", {"min": 0, "max": 10})
                    
                    # Extract score and justification
                    if self.config.include_justification:
                        score, justification = self._extract_metric_data(response, metric)
                        result["justifications"][metric] = self._validate_justification(
                            justification, metric, result["validation_issues"]
                        )
                    else:
                        score = self._extract_score(response, metric)
                    
                    # Validate score against criteria if available
                    if "scoring_criteria" in metric_config:
                        score = self._validate_against_criteria(
                            score, 
                            metric_config["scoring_criteria"],
                            metric,
                            result["validation_issues"]
                        )
                    
                    # Validate and normalize score
                    score = self._validate_score(
                        score, 
                        score_range["min"], 
                        score_range["max"],
                        metric,
                        result["validation_issues"]
                    )
                    normalized_score = self._normalize_score(score, score_range["min"], score_range["max"])
                    
                    # Store results
                    result["raw_scores"][metric] = score
                    result["normalized_scores"][metric] = normalized_score
                    
                    total_weighted_score += normalized_score * weight
                    total_weight += weight
                    
                except Exception as e:
                    logging.error(f"Error processing metric {metric}: {str(e)}")
                    result["validation_issues"].append(f"Failed to process metric {metric}: {str(e)}")
                    result["raw_scores"][metric] = 0
                    result["normalized_scores"][metric] = 0
                    if self.config.include_justification:
                        result["justifications"][metric] = f"Error: {str(e)}"
            
            # Calculate final weighted score
            result["total_weighted_score"] = (
                total_weighted_score / total_weight if total_weight > 0 else 0
            )
            
            # Add metadata
            result["metadata"] = {
                "task_type": task_type,
                "num_metrics_processed": len(task_config["weightages"]),
                "num_validation_issues": len(result["validation_issues"]),
                "total_weight": total_weight,
                "include_justification": self.config.include_justification
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Error parsing evaluation response: {str(e)}")
            raise ValueError(f"Failed to parse evaluation response: {str(e)}")
    
    def _extract_score(self, response: str, metric: str) -> float:
        """Extract score for a metric from response"""
        try:
            score_pattern = rf"{metric.upper()}_SCORE:\s*(\d+(?:\.\d+)?)"
            score_match = re.search(score_pattern, response)
            
            if not score_match:
                raise ValueError(f"Could not find score for metric {metric}")
            
            return float(score_match.group(1))
            
        except Exception as e:
            logging.error(f"Error extracting score: {str(e)}")
            return 0.0
    
    def _extract_metric_data(self, response: str, metric: str) -> Tuple[float, str]:
        """Extract score and justification for a metric from response"""
        score = self._extract_score(response, metric)
        
        try:
            # Look for justification pattern
            justification_pattern = rf"{metric.upper()}_JUSTIFICATION:\s*(.+?)(?=\w+_(?:SCORE|JUSTIFICATION):|$)"
            justification_match = re.search(justification_pattern, response, re.DOTALL)
            
            justification = justification_match.group(1).strip() if justification_match else "No justification provided"
            return score, justification
            
        except Exception as e:
            logging.error(f"Error extracting justification: {str(e)}")
            return score, f"Error extracting justification: {str(e)}"
    
    def _validate_score(self, score: float, min_score: float, max_score: float, 
                       metric: str, issues: List[str]) -> float:
        """Validate score is within allowed range"""
        if score < min_score:
            issues.append(f"Score {score} for {metric} below minimum {min_score}, using minimum")
            return min_score
        if score > max_score:
            issues.append(f"Score {score} for {metric} above maximum {max_score}, using maximum")
            return max_score
        return score
    
    def _validate_against_criteria(self, score: float, criteria: Dict[str, str],
                                 metric: str, issues: List[str]) -> float:
        """Validate score against defined criteria"""
        valid_scores = [float(s) for s in criteria.keys()]
        if score not in valid_scores:
            closest_score = min(valid_scores, key=lambda x: abs(x - score))
            issues.append(
                f"Score {score} for {metric} not in valid scores {valid_scores}, "
                f"using closest value {closest_score}"
            )
            return closest_score
        return score
    
    def _validate_justification(self, justification: str, metric: str,
                              issues: List[str]) -> str:
        """Validate justification content"""
        if not justification:
            issues.append(f"Empty justification for {metric}")
            return "No justification provided"
        if len(justification) < 10:
            issues.append(f"Very short justification for {metric}")
        return justification
    
    def _normalize_score(self, score: float, min_score: float, max_score: float) -> float:
        """Normalize score to 0-1 range"""
        if max_score == min_score:
            return 1.0 if score >= max_score else 0.0
        return (score - min_score) / (max_score - min_score)
