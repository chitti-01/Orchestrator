from orchestrator.core.task_graph import TaskNode

class EscalationManager:
    """
    Escalates task node model tier upon repeated execution or verification failures (M1 -> M2 -> M3).
    """
    def __init__(self):
        self.escalation_map = {
            "model_1": "model_2",
            "model_2": "model_3",
            "model_3": "model_3"
        }

    def escalate_node(self, node: TaskNode) -> str:
        current_model = node.selected_model
        next_model = self.escalation_map.get(current_model, "model_3")
        node.selected_model = next_model
        return next_model
