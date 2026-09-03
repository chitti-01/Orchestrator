import pytest
from orchestrator.analysis.deterministic_analyzer import DeterministicAnalyzer
from orchestrator.planning.planner import TaskPlanner

@pytest.fixture
def analyzer():
    return DeterministicAnalyzer()

@pytest.fixture
def planner():
    return TaskPlanner()

def test_planner_single_node(analyzer, planner):
    reqs = analyzer.analyze("Reverse a string in Python.")
    graph, latency = planner.plan_workflow(reqs, 20.0, ["Routine query"])
    
    assert len(graph.nodes) == 1
    node = list(graph.nodes.values())[0]
    assert node.selected_model == "model_1"

def test_planner_dag_decomposition(analyzer, planner):
    reqs = analyzer.analyze("Build a production payment platform with authentication, transaction processing, fraud detection, database replication, fault tolerance and PCI compliance.")
    graph, latency = planner.plan_workflow(reqs, 88.0, ["Complex platform"])
    
    assert len(graph.nodes) > 1
    root = list(graph.nodes.values())[0]
    assert len(root.dependencies) == 0
