import json
import logging
import re
from pathlib import Path
from typing import Dict, Optional, Tuple
from lsada.config.config_manager import config_manager

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
                "raw_scores": {}
            }
            
            if include_justification:
                result["justifications"] = {}

            # Process each metric
            for metric, weight in task_config["weightages"].items():
                try:
                    # Extract score and justification
                    if include_justification:
                        score, justification = self._extract_metric_data(response, metric)
                        result["justifications"][metric] = justification
                    else:
                        score = self._extract_score(response, metric)

                    result["raw_scores"][metric] = score
                
                except Exception as e:
                    logging.error(f"Error processing metric {metric}: {str(e)}")
                    result["validation_issues"].append(f"Error processing metric {metric}: {str(e)}")
                
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
            
    def _extract_score(self, response: str, metric: str) -> float:
        """Extract score for a metric from response"""
        try:
            # Look for score pattern: METRIC_SCORE: number
            score_pattern = rf"{metric.upper()}_SCORE:\s*(\d+(?:\.\d+)?)"
            score_match = re.search(score_pattern, response)
            
            if not score_match:
                raise ValueError(f"Could not find score for metric {metric}")
            score = float(score_match.group(1))
            return score
            
        except Exception as e:
            logging.error(f"Error extracting score: {str(e)}")
            return 0.0