"""
LSADA - Language Services and Data Analysis
A flexible evaluation framework for content using LLMs
"""

__version__ = "1.0.0"

from .evaluator.evaluator import Evaluator
from .models.llm_manager import LLMManager, BaseLLMClient
from .config.config_manager import config_manager
from .utils.metrics import MetricsCalculator
from .utils.llm_parser import LLMResponseParser
from .evaluator.task_manager import TaskManager 

__all__ = [
    'Evaluator',
    'LLMManager',
    'BaseLLMClient',
    'ConfigManager',
    'config_manager',
    'MetricsCalculator',
    'LLMResponseParser',
    'TaskManager'
]
