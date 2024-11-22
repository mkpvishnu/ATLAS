import logging
from typing import Dict

class LLMResponseParser:
    @staticmethod
    def parse_evaluation_response(response_text: str, metrics: list[str]) -> Dict:
        """Parse LLM response for any evaluation type based on expected metrics"""
        try:
            lines = response_text.split('\n')
            evaluation = {}
            
            for line in lines:
                if ':' not in line:
                    continue
                    
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                # Check if this is a score line
                if key.endswith('_score'):
                    try:
                        evaluation[key] = float(value)
                    except ValueError:
                        logging.warning(f"Could not parse score for {key}: {value}")
                        evaluation[key] = 0
                # Check if this is a justification line
                elif key.endswith('_justification'):
                    evaluation[key] = value

            # Validate all required metrics are present
            for metric in metrics:
                score_key = f"{metric}_score"
                justification_key = f"{metric}_justification"
                
                if score_key not in evaluation:
                    logging.error(f"Missing score for metric: {metric}")
                    evaluation[score_key] = 0
                if justification_key not in evaluation:
                    logging.error(f"Missing justification for metric: {metric}")
                    evaluation[justification_key] = "No justification provided"
                    
            return evaluation
            
        except Exception as e:
            logging.error(f"Error parsing LLM response: {str(e)}")
            raise
