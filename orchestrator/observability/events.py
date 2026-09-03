import time
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field

logger = logging.getLogger("orchestrator.events")

class OrchestrationEvent(BaseModel):
    event_type: str
    workflow_id: str
    timestamp: float = Field(default_factory=time.time)
    details: Dict[str, Any] = Field(default_factory=dict)

class EventTracker:
    def __init__(self):
        self.events: List[OrchestrationEvent] = []

    def emit(self, event_type: str, workflow_id: str, details: Dict[str, Any]):
        evt = OrchestrationEvent(event_type=event_type, workflow_id=workflow_id, details=details)
        self.events.append(evt)
        logger.info(f"[{workflow_id}] {event_type}: {details}")

    def get_events(self) -> List[OrchestrationEvent]:
        return list(self.events)
