"""
LSADA Pool Module - Contains configuration pools for tasks and metrics
"""

import os
from pathlib import Path

# Get the absolute path to the data directory
_data_dir = Path(__file__).parent

# Define paths to JSON files
task_pool = _data_dir / "task_pool.json"
metrics_pool = _data_dir / "metrics_pool.json"

__all__ = ["task_pool", "metrics_pool"]