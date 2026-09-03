import asyncio
import time
from typing import List, Dict, Any
from orchestrator.core.task_graph import TaskGraph, TaskNode
from orchestrator.execution.executor import ModelExecutor
from orchestrator.context.manager import ContextManager
from orchestrator.analysis.requirements import TaskRequirements

class AsyncScheduler:
    """
    Executes ready DAG task graph nodes in parallel using asyncio where dependencies permit.
    """
    def __init__(self, executor: ModelExecutor, context_manager: ContextManager):
        self.executor = executor
        self.context_manager = context_manager

    async def execute_graph(self, graph: TaskGraph, reqs: TaskRequirements) -> List[TaskNode]:
        executed_nodes: List[TaskNode] = []

        while not graph.is_complete():
            ready_nodes = graph.get_ready_nodes()
            if not ready_nodes:
                # Break deadlock if any
                break

            # Execute all ready nodes concurrently
            tasks = [
                self._execute_single_node(node, graph, reqs)
                for node in ready_nodes
            ]
            results = await asyncio.gather(*tasks)
            executed_nodes.extend(results)

        return executed_nodes

    async def _execute_single_node(self, node: TaskNode, graph: TaskGraph, reqs: TaskRequirements) -> TaskNode:
        node.status = "running"
        pkg = self.context_manager.build_package_for_node(node, graph, reqs)

        exec_res = await self.executor.execute(node.selected_model, pkg)
        
        node.execution_time_ms = exec_res.latency_ms
        if exec_res.success:
            node.status = "completed"
            node.result = exec_res.output
            self.context_manager.record_node_result(node.task_id, exec_res.output)
        else:
            node.status = "failed"
            node.result = exec_res.error or "Execution failed"

        return node
