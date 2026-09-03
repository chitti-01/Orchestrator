import json
from pathlib import Path
from typing import Dict, Any, Optional

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"

class PolicyEngine:
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or CONFIG_DIR
        self.routing_path = self.config_dir / "routing.json"
        self.policies_path = self.config_dir / "policies.json"
        self.execution_path = self.config_dir / "execution.json"
        
        self.routing_config = self._load_json(self.routing_path)
        self.policies_config = self._load_json(self.policies_path)
        self.execution_config = self._load_json(self.execution_path)

    def _load_json(self, path: Path) -> Dict[str, Any]:
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get_thresholds(self) -> Dict[str, float]:
        return self.routing_config.get("thresholds", {
            "model_1_max_score": 29.0,
            "model_2_max_score": 68.0
        })

    def get_capability_weights(self) -> Dict[str, float]:
        return self.routing_config.get("capability_weights", {
            "reasoning": 0.28, "coding": 0.22, "planning": 0.20,
            "architecture": 0.18, "tool_use": 0.12
        })

    def get_recovery_policy(self) -> Dict[str, Any]:
        return self.policies_config.get("recovery", {
            "max_retries": 3, "escalate_on_failure": True,
            "escalation_map": {"model_1": "model_2", "model_2": "model_3", "model_3": "model_3"},
            "allow_replanning": True
        })

    def get_concurrency_policy(self) -> Dict[str, Any]:
        return self.policies_config.get("concurrency", {
            "max_parallel_subtasks": 5, "task_timeout_seconds": 30.0
        })
