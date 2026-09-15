import json
from pathlib import Path
from typing import Dict, Optional, List
from orchestrator.models.profile import ModelCapabilityProfile
from orchestrator.models.capabilities import ModelCapabilities, ModelCost

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"

class ModelRegistry:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (CONFIG_DIR / "models.json")
        self._models: Dict[str, ModelCapabilityProfile] = {}
        self.load_models()

    def load_models(self):
        if not self.config_path.exists():
            self._models = self._default_models()
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            data = json.load(f).get("models", {})

        self._models.clear()
        for key, m_data in data.items():
            caps = ModelCapabilities(**m_data["capabilities"])
            cost = ModelCost(**m_data.get("cost", {}))
            profile = ModelCapabilityProfile(
                id=m_data["id"],
                name=m_data["name"],
                tier=m_data["tier"],
                provider=m_data.get("provider", "openai"),
                model_name=m_data.get("model_name", m_data["id"]),
                api_key_env=m_data.get("api_key_env"),
                api_base_env=m_data.get("api_base_env"),
                api_base=m_data.get("api_base"),
                description=m_data.get("description", ""),
                capabilities=caps,
                cost=cost,
                latency_class=m_data.get("latency_class", "fast"),
                specializations=m_data.get("specializations", [])
            )
            self._models[key] = profile

    def get_model(self, model_id: str) -> Optional[ModelCapabilityProfile]:
        return self._models.get(model_id)

    def get_model_by_tier(self, tier: str) -> Optional[ModelCapabilityProfile]:
        for model in self._models.values():
            if model.tier.lower() == tier.lower():
                return model
        return None

    def list_models(self) -> Dict[str, ModelCapabilityProfile]:
        return self._models.copy()

    def _default_models(self) -> Dict[str, ModelCapabilityProfile]:
        return {
            "model_1": ModelCapabilityProfile(
                id="model_1", name="Model 1 (Simple)", tier="simple",
                provider="openai", model_name="gpt-4o-mini", api_key_env="MODEL_1_API_KEY",
                capabilities=ModelCapabilities(
                    reasoning=0.40, planning=0.30, architecture=0.25, implementation=0.45, coding=0.45,
                    security=0.30, distributed_systems=0.20, data_modeling=0.35, integration=0.35, testing=0.40,
                    documentation=0.80, summarization=0.90, context_handling=0.50, tool_use=0.40, verification=0.40,
                    mathematics=0.30, multimodal=False, reliability=0.95, context_window=16000
                ),
                cost=ModelCost(input_per_1k=0.0005, output_per_1k=0.0015), latency_class="fast"
            ),
            "model_2": ModelCapabilityProfile(
                id="model_2", name="Model 2 (Medium)", tier="medium",
                provider="openai", model_name="gpt-4o", api_key_env="MODEL_2_API_KEY",
                capabilities=ModelCapabilities(
                    reasoning=0.70, planning=0.65, architecture=0.65, implementation=0.80, coding=0.85,
                    security=0.65, distributed_systems=0.60, data_modeling=0.75, integration=0.75, testing=0.75,
                    documentation=0.85, summarization=0.90, context_handling=0.75, tool_use=0.80, verification=0.75,
                    mathematics=0.70, multimodal=True, reliability=0.96, context_window=64000
                ),
                cost=ModelCost(input_per_1k=0.003, output_per_1k=0.009), latency_class="balanced"
            ),
            "model_3": ModelCapabilityProfile(
                id="model_3", name="Model 3 (Complex)", tier="complex",
                provider="openai", model_name="gpt-4o", api_key_env="MODEL_3_API_KEY",
                capabilities=ModelCapabilities(
                    reasoning=0.98, planning=0.98, architecture=0.98, implementation=0.95, coding=0.95,
                    security=0.95, distributed_systems=0.98, data_modeling=0.95, integration=0.95, testing=0.95,
                    documentation=0.95, summarization=0.95, context_handling=0.95, tool_use=0.95, verification=0.95,
                    mathematics=0.95, multimodal=True, reliability=0.99, context_window=128000
                ),
                cost=ModelCost(input_per_1k=0.015, output_per_1k=0.045), latency_class="high_capability"
            )
        }

