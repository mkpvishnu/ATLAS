import json
import logging
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    """Singleton class to manage all configuration loading"""
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self._base_path = Path(__file__).parent.parent
            self._load_configs()
            
    def _load_configs(self):
        """Load all configuration files"""
        try:
            # Load task pool
            with open(self._base_path / "pool" / "task_pool.json", "r") as f:
                self.task_pool = json.load(f)
                
            # Load metrics pool
            with open(self._base_path / "pool" / "metrics_pool.json", "r") as f:
                self.metrics_pool = json.load(f)
                
            logging.info("Successfully loaded all configuration files")
        except Exception as e:
            logging.error(f"Error loading configuration files: {str(e)}")
            raise
        
    def get_metrics_config(self, metric_name: str) -> Dict[str, Any]:
        """Get configuration for a specific metric"""
        # Search through all metric groups
        if metric_name in self.metrics_pool.keys():
            return self.metrics_pool[metric_name]
                
        raise ValueError(f"Unknown metric: {metric_name}")
        
    def get_task_config(self, task_type: str) -> Dict[str, Any]:
        """Get configuration for a specific task type"""
        if task_type not in self.task_pool["task_types"].keys():
            print(self.task_pool["task_types"].keys())
            raise ValueError(f"Unknown task type: {task_type}")
            
        return self.task_pool["task_types"][task_type]

# Global instance
config_manager = ConfigManager()
