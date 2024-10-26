from flask import Flask, request, jsonify
import requests
from typing import List, Dict
import statistics
import numpy as np
from dataclasses import dataclass
from datetime import datetime
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Constants
LLM_API_URL = "https://cloudverse.freshworkscorp.com/api/chat"
DEFAULT_EVALUATIONS = 5

@dataclass
class ConversationTurn:
    user_message: str
    llm_response: str

class ConversationEvaluator:
    def __init__(self, num_evaluations: int = DEFAULT_EVALUATIONS):
        self.num_evaluations = num_evaluations
        self.evaluation_criteria = self._load_evaluation_criteria()
        
    def _load_evaluation_criteria(self) -> Dict:
        return {
            "coherence": {
                25: "Perfect flow, natural transitions, and clear logical progression",
                20: "Strong coherence with minor inconsistencies",
                15: "Adequate coherence but some awkward transitions",
                10: "Notable gaps in coherence",
                5: "Significant coherence issues"
            },
            "relevance": {
                25: "Responses directly address users needs with precise information",
                20: "Mostly relevant with minor tangents",
                15: "Generally relevant but some off-topic elements",
                10: "Significant irrelevant content",
                5: "Mostly irrelevant responses"
            },
            "helpfulness": {
                25: "Exceptional assistance, going above and beyond",
                20: "Very helpful with good solutions",
                15: "Moderately helpful",
                10: "Minimal help provided",
                5: "Not helpful or misleading"
            },
            "context_awareness": {
                15: "Perfect recall and use of conversation history",
                10: "Good context awareness with minor misses",
                5: "Poor context awareness"
            },
            "consistency": {
                10: "Perfect consistency in tone, information, and approach",
                7: "Minor consistency issues",
                3: "Major consistency issues"
            }
        }

    def generate_evaluation_prompt(self, conversation: str) -> str:
        prompt = f"""You are an expert conversation evaluator. Evaluate the following multi-turn conversation based on these specific criteria:

1. Coherence (25 points):
{self._format_criteria("coherence")}

2. Relevance (25 points):
{self._format_criteria("relevance")}

3. Helpfulness (25 points):
{self._format_criteria("helpfulness")}

4. Context Awareness (15 points):
{self._format_criteria("context_awareness")}

5. Consistency (10 points):
{self._format_criteria("consistency")}

Conversation to evaluate:
{conversation}

Provide your evaluation in the following format exactly:
COHERENCE_SCORE: [number]
COHERENCE_JUSTIFICATION: [text]
RELEVANCE_SCORE: [number]
RELEVANCE_JUSTIFICATION: [text]
HELPFULNESS_SCORE: [number]
HELPFULNESS_JUSTIFICATION: [text]
CONTEXT_AWARENESS_SCORE: [number]
CONTEXT_AWARENESS_JUSTIFICATION: [text]
CONSISTENCY_SCORE: [number]
CONSISTENCY_JUSTIFICATION: [text]
"""
        return prompt

    def _format_criteria(self, criteria_name: str) -> str:
        return "\n".join([
            f"Score {score}: {description}"
            for score, description in self.evaluation_criteria[criteria_name].items()
        ])

    def _call_llm_api(self, prompt: str) -> Dict:
        """Call the LLM API and parse the response"""
        try:
            payload = {
                "messages": [
                    {
                        "content": prompt,
                        "role": "user"
                    }
                ],
                "model": "Azure-GPT-4o-mini",
                "temperature": 0,
                "top_p": 0,
                "frequency_penalty": 0,
                "presence_penalty": 0,
                "stop": [],
                "max_tokens": 4096,
                "system_instructions": "You are an AI assistant that helps evaluate conversations."
            }
            print(payload)
            
            response = requests.post(LLM_API_URL, json=payload,verify=False, headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjp7Im5hbWUiOiJQcmFnYWRlc2h3YXIgVmlzaG51IiwiZW1haWwiOiJwcmFnYWRlc2h3YXIudmlzaG51MUBmcmVzaHdvcmtzLmNvbSIsImltYWdlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tL2EvQUNnOG9jTHlSUU9RNjBxOE5ZWFdfTmJSMWdDNW5PazVLWkVlNmJ0TFVUaWkxRVROSlJQYUJxUT1zOTYtYyJ9LCJqdGkiOiJCajNSSVZSR3VmWnF0RXM3R2pveUEiLCJpYXQiOjE3MjkzNjcwMjYsImV4cCI6MTcyOTk3MTgyNn0.Yna8Wi3fDQ-We-DSzQbzPUYZSSsHypT6BVTrwvo6uNs"})
            response.raise_for_status()
            print(response.json())
            
            # Parse the response text to extract scores and justifications
            response_text = response.json()["choices"][0]["message"]["content"]
            return self._parse_llm_response(response_text)
            
        except Exception as e:
            logging.error(f"Error calling LLM API: {str(e)}")
            raise

    def _parse_llm_response(self, response_text: str) -> Dict:
        """Parse the LLM response into structured data"""
        try:
            lines = response_text.split('\n')
            evaluation = {}
            
            for line in lines:
                if ':' not in line:
                    continue
                    
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                if '_SCORE' in key:
                    try:
                        evaluation[key.lower()] = float(value)
                    except ValueError:
                        logging.warning(f"Could not parse score for {key}: {value}")
                        evaluation[key.lower()] = 0
                elif '_JUSTIFICATION' in key:
                    evaluation[key.lower()] = value
                    
            return evaluation
            
        except Exception as e:
            logging.error(f"Error parsing LLM response: {str(e)}")
            raise

    def evaluate_conversation(self, conversation: str) -> Dict:
        all_evaluations = []
        
        # Perform multiple evaluations
        for i in range(self.num_evaluations):
            logging.info(f"Performing evaluation {i+1}/{self.num_evaluations}")
            prompt = self.generate_evaluation_prompt(conversation)
            evaluation = self._call_llm_api(prompt)
            all_evaluations.append(evaluation)
        
        # Aggregate and filter results
        final_scores = self._aggregate_scores(all_evaluations)
        
        return {
            "final_scores": final_scores,
            "confidence": self._calculate_confidence(all_evaluations),
            "evaluation_metadata": {
                "num_evaluations": self.num_evaluations,
                "timestamp": datetime.now().isoformat()
            }
        }

    def _aggregate_scores(self, evaluations: List[Dict]) -> Dict:
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
            
            aggregated[metric] = {
                "score": statistics.median(filtered_scores),
                "variance": statistics.variance(filtered_scores) if len(filtered_scores) > 1 else 0,
                "sample_justification": justifications[0]  # Include one sample justification
            }
        
        return aggregated

    def _calculate_confidence(self, evaluations: List[Dict]) -> float:
        metrics = ["coherence", "relevance", "helpfulness", "context_awareness", "consistency"]
        variances = []
        
        for metric in metrics:
            score_key = f"{metric}_score"
            scores = [eval.get(score_key, 0) for eval in evaluations]
            if len(scores) > 1:
                variances.append(statistics.variance(scores))
        
        avg_variance = statistics.mean(variances) if variances else 0
        confidence = 1 / (1 + avg_variance)
        return round(confidence, 2)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json
        
        if not data.get('content'):
            return jsonify({"error": "No conversation content provided"}), 400
            
        num_evaluations = data.get('num_of_evaluations', DEFAULT_EVALUATIONS)
        task_type = data.get('task_type', 'conversation_evaluation')
        
        if task_type != 'conversation_evaluation':
            return jsonify({"error": "Unsupported task type"}), 400
            
        evaluator = ConversationEvaluator(num_evaluations=num_evaluations)
        results = evaluator.evaluate_conversation(data['content'])
        
        return jsonify(results)
        
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)