import pytest
from orchestrator import Orchestrator

@pytest.fixture
def orchestrator():
    return Orchestrator()

def test_critical_case_1_hello_world(orchestrator):
    # "Create a hello world website." -> 1 Task, Model 1
    res = orchestrator.run_sync("Create a hello world website.")
    assert res.selected_model == "model_1"
    assert len(res.plan_nodes) == 1

def test_critical_case_2_bst_explain(orchestrator):
    # "Explain how a binary search tree works." -> 1 Task, Model 1
    res = orchestrator.run_sync("Explain how a binary search tree works.")
    assert res.selected_model == "model_1"
    assert len(res.plan_nodes) == 1

def test_critical_case_3_rest_api(orchestrator):
    # "Implement a REST API for user registration..." -> Model 2
    res = orchestrator.run_sync("Implement a REST API for user registration with validation and database persistence.")
    assert res.selected_model in ["model_2", "model_3"]

def test_critical_case_4_distributed_database(orchestrator):
    # "Design a fault-tolerant, multi-region distributed database..."
    prompt = "Design a fault-tolerant, multi-region distributed database that provides globally consistent transactions under network partitions, supports horizontal scaling without downtime, guarantees recovery after simultaneous regional failures, and maintains correctness under concurrent writes."
    res = orchestrator.run_sync(prompt)
    
    assert res.selected_model == "model_3"
    assert len(res.plan_nodes) > 3  # Requirement-derived dynamic DAG tasks
    
    # Verify requirement-derived task names (NO generic "Backend Core Service")
    task_names = [n["name"] for n in res.plan_nodes]
    assert not any("Backend Core Service" in name for name in task_names)
    assert any("Globally Consistent Transactions" in name for name in task_names)
    assert any("Network Partition Tolerance" in name for name in task_names)

def test_critical_case_5_payment_explain(orchestrator):
    # "Explain what a payment gateway is." -> Model 1
    res = orchestrator.run_sync("Explain what a payment gateway is.")
    assert res.selected_model == "model_1"
    assert len(res.plan_nodes) == 1

def test_critical_case_6_payment_build(orchestrator):
    # "Build a production payment gateway." -> Model 2 / Model 3
    res = orchestrator.run_sync("Build a production payment gateway.")
    assert res.selected_model in ["model_2", "model_3"]

def test_critical_case_7_math_theorem_proof(orchestrator):
    # "Prove a difficult mathematical theorem." -> Model 3
    res = orchestrator.run_sync("Prove a difficult mathematical theorem.")
    assert res.selected_model == "model_3"

def test_critical_case_8_long_but_simple_summary(orchestrator):
    # Long text asking only to summarize -> Model 1
    long_text = "Summarize this document: " + ("The brown fox jumped over the lazy dog. " * 50)
    res = orchestrator.run_sync(long_text)
    assert res.selected_model == "model_1"

def test_critical_case_9_short_but_complex(orchestrator):
    # Short prompt: "Design a consensus protocol that remains safe during network partitions." -> Model 3
    res = orchestrator.run_sync("Design a consensus protocol that remains safe during network partitions.")
    assert res.selected_model == "model_3"
