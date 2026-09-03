from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from orchestrator.analysis.requirements import RequirementItem

class RequirementGraph(BaseModel):
    raw_prompt: str
    items: Dict[str, RequirementItem] = Field(default_factory=dict)
    relationships: List[Dict[str, str]] = Field(default_factory=list)

    def add_item(self, item: RequirementItem):
        self.items[item.id] = item

    def add_relationship(self, source_id: str, target_id: str, rel_type: str):
        if source_id in self.items and target_id in self.items:
            if target_id not in self.items[source_id].dependencies:
                self.items[source_id].dependencies.append(target_id)
            self.relationships.append({
                "source": source_id,
                "target": target_id,
                "type": rel_type
            })
