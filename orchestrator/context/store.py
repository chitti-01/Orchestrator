from typing import Dict, Any, Optional

class ContextStore:
    """
    Global Workflow State Store holding task execution outputs and shared artifacts.
    """
    def __init__(self):
        self._results: Dict[str, str] = {}
        self._artifacts: Dict[str, Any] = {}

    def save_result(self, task_id: str, result: str):
        self._results[task_id] = result

    def get_result(self, task_id: str) -> Optional[str]:
        return self._results.get(task_id)

    def save_artifact(self, name: str, data: Any):
        self._artifacts[name] = data

    def get_artifact(self, name: str) -> Optional[Any]:
        return self._artifacts.get(name)

    def clear(self):
        self._results.clear()
        self._artifacts.clear()
