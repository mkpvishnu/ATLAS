from typing import Dict, Optional, Union
from pydantic import BaseModel, Field

class ModelConfig(BaseModel):
    """Configuration for LLM models"""
    provider: str = Field(..., description="Model provider (e.g., 'openai', 'anthropic')")
    model_name: str = Field(..., description="Name of the model to use")
    api_key: Optional[str] = Field(None, description="API key for the model provider")
    additional_params: Dict = Field(default_factory=dict, description="Additional model-specific parameters")

class EvaluationConfig(BaseModel):
    """Configuration for evaluation settings"""
    task_type: Optional[str] = Field(None, description="Type of task to evaluate")
    num_evaluations: int = Field(default=1, description="Number of evaluations to perform")
    include_justification: bool = Field(default=True, description="Whether to include justification in evaluation")
    model: ModelConfig = Field(..., description="Model configuration")
    temperature: float = Field(default=0.0, description="Temperature for model generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for model response")

class MetricConfig(BaseModel):
    """Configuration for evaluation metrics"""
    name: str = Field(..., description="Name of the metric")
    description: str = Field(..., description="Description of what the metric measures")
    weight: float = Field(..., ge=0, le=1, description="Weight of the metric in overall score")
    score_range: Dict[str, float] = Field(
        default={"min": 0, "max": 10},
        description="Valid score range for this metric"
    )
    scoring_criteria: Optional[Dict[str, str]] = Field(
        None,
        description="Mapping of scores to their criteria"
    )
