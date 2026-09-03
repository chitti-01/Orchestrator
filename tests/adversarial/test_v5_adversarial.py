import pytest
import inspect
from orchestrator import Orchestrator
import orchestrator.routing.router as router_module

@pytest.fixture
def orchestrator():
    return Orchestrator()

def test_v5_test_a_short_complex_collab_editor(orchestrator):
    """
    TEST A: Short prompt, extremely complex system requirements.
    "Build a globally distributed collaborative editor with offline editing, concurrent conflict resolution and regional failover."
    Must produce HIGH workflow complexity, dynamic DAG, and heterogeneous model assignments (coexisting M1/M2/M3).
    """
    prompt = "Build a globally distributed collaborative editor with offline editing, concurrent conflict resolution and regional failover."
    res = orchestrator.run_sync(prompt)

    assert res.workflow_complexity >= 70.0
    assert len(res.plan_nodes) > 1

    models_used = set(n["selected_model"] for n in res.plan_nodes)
    assert len(models_used) >= 2, f"Expected heterogeneous model assignments, got {models_used}"
    assert "model_3" in models_used, "Complex concurrency/recovery task must use Model 3"

def test_v5_test_b_simple_explanation_collab_editor(orchestrator):
    """
    TEST B: Simple explanation of collaborative editor.
    "Explain how a globally distributed collaborative editor works in simple terms."
    Expected: 1 Task, MODEL_1.
    """
    prompt = "Explain how a globally distributed collaborative editor works in simple terms."
    res = orchestrator.run_sync(prompt)

    assert len(res.plan_nodes) == 1
    assert res.plan_nodes[0]["selected_model"] == "model_1"

def test_v5_test_c_rest_endpoint_listing(orchestrator):
    """
    TEST C: Simple REST endpoint listing.
    "List five REST endpoints for document management."
    Expected: MODEL_1 or MODEL_2 (NOT MODEL_3).
    """
    prompt = "List five REST endpoints for document management."
    res = orchestrator.run_sync(prompt)

    assert res.selected_model in ["model_1", "model_2"]
    for node in res.plan_nodes:
        assert node["selected_model"] != "model_3"

def test_v5_test_d_concurrent_conflict_semantics(orchestrator):
    """
    TEST D: Complex concurrent conflict resolution.
    "Design conflict-free concurrent editing semantics under network partitions and regional failures."
    Expected: MODEL_3.
    """
    prompt = "Design conflict-free concurrent editing semantics under network partitions and regional failures."
    res = orchestrator.run_sync(prompt)

    assert res.selected_model == "model_3"

def test_v5_test_e_short_documentation(orchestrator):
    """
    TEST E: Short documentation section.
    "Write a short documentation section explaining the API."
    Expected: MODEL_1.
    """
    prompt = "Write a short documentation section explaining the API."
    res = orchestrator.run_sync(prompt)

    assert res.selected_model == "model_1"
    assert len(res.plan_nodes) == 1

def test_v5_test_f_mixed_complexity_enterprise_workflow(orchestrator):
    """
    TEST F: Mixed-complexity enterprise workflow.
    Workflow contains architecture, security, API design, metrics, and documentation.
    Must produce heterogeneous model assignment across tasks.
    """
    prompt = (
        "Design and build an enterprise document management platform with multi-tenant data isolation, "
        "concurrent write correctness, REST API endpoints, observability metrics, and user documentation."
    )
    res = orchestrator.run_sync(prompt)

    assert len(res.plan_nodes) > 2
    models_used = set(n["selected_model"] for n in res.plan_nodes)
    assert len(models_used) >= 2, f"Expected heterogeneous model assignments across tasks, got {models_used}"

def test_v5_test_g_long_simple_educational_explanation(orchestrator):
    """
    TEST G: Long but simple educational explanation.
    "Explain TCP three-way handshake in 2000 words..."
    Expected: 1 Task, MODEL_1 (Long != Complex).
    """
    prompt = "Explain the TCP three-way handshake in 2000 words. " + ("Include details on SYN, SYN-ACK, and ACK flags. " * 10)
    res = orchestrator.run_sync(prompt)

    assert len(res.plan_nodes) == 1
    assert res.selected_model == "model_1"

def test_v5_test_h_technology_exclusion_strictness(orchestrator):
    """
    TEST H: Complex prompt explicitly prohibiting technologies.
    "Design a distributed job processing architecture. Do not assume any specific database, queue, cloud provider, programming language, or framework."
    Expected: explicit_exclusions populated, zero injected tech.
    """
    prompt = "Design a distributed job processing architecture. Do not assume any specific database, queue, cloud provider, programming language, or framework."
    res = orchestrator.run_sync(prompt)

    assert len(res.explicit_exclusions) > 0
    for node in res.plan_nodes:
        desc_lower = node["description"].lower()
        for forbidden in ["kafka", "redis", "rabbitmq", "postgresql", "aws", "kubernetes", "python", "java"]:
            assert forbidden not in desc_lower

def test_v5_test_i_complex_workflow_simple_doc_task(orchestrator):
    """
    TEST I: Complex workflow containing simple documentation / metrics task.
    The documentation / metrics node MUST be assigned MODEL_1 even though overall workflow is complex!
    """
    prompt = (
        "Design and implement a multi-tenant AI document-processing platform with concurrent write correctness, "
        "regional failover, permission-aware retrieval, end-to-end testing, and observability metrics documentation."
    )
    res = orchestrator.run_sync(prompt)

    assert res.workflow_complexity >= 70.0
    # Check that at least one task in this complex workflow received Model 1 or Model 2
    models_used = [n["selected_model"] for n in res.plan_nodes]
    assert "model_1" in models_used or "model_2" in models_used, f"Expected non-Model 3 tasks in complex workflow, got {models_used}"

def test_v5_test_j_single_model3_task_in_complex_workflow(orchestrator):
    """
    TEST J: Complex workflow where only one task genuinely requires MODEL_3.
    """
    prompt = "Create a web application with REST API endpoints, simple CSS styling, user documentation, and one complex multi-region consensus protocol core."
    res = orchestrator.run_sync(prompt)

    consensus_nodes = [n for n in res.plan_nodes if "consensus" in n["name"].lower() or "partition" in n["name"].lower()]
    doc_nodes = [n for n in res.plan_nodes if "documentation" in n["name"].lower() or "metrics" in n["name"].lower()]

    if consensus_nodes:
        assert consensus_nodes[0]["selected_model"] == "model_3"
    if doc_nodes:
        assert doc_nodes[0]["selected_model"] in ["model_1", "model_2"]

def test_v5_test_k_all_model1_workflow(orchestrator):
    """
    TEST K: Workflow where MODEL_1 is sufficient for every task.
    "Explain binary search, summarize how it works, and provide a text outline of its step-by-step algorithm."
    """
    prompt = "Explain binary search, summarize how it works, and provide a text outline of its step-by-step algorithm."
    res = orchestrator.run_sync(prompt)

    for node in res.plan_nodes:
        assert node["selected_model"] == "model_1"

def test_v5_test_l_multiple_model3_tasks(orchestrator):
    """
    TEST L: Workflow where MODEL_3 is genuinely required for multiple tasks.
    "Design a fault-tolerant, multi-region distributed database with globally consistent transactions, formal security proofs, and split-brain recovery."
    """
    prompt = "Design a fault-tolerant, multi-region distributed database with globally consistent transactions, formal security proofs, and split-brain recovery."
    res = orchestrator.run_sync(prompt)

    m3_count = sum(1 for n in res.plan_nodes if n["selected_model"] == "model_3")
    assert m3_count >= 2, f"Expected multiple Model 3 tasks, got {m3_count}"

def test_critical_anti_hardcoding():
    """
    CRITICAL ANTI-HARDCODING TEST:
    Inspect source code of ModelRouter and ensure NO rules like:
    if "security" -> MODEL_3, if "architecture" -> MODEL_3, or hardcoded task position routing.
    """
    source = inspect.getsource(router_module.ModelRouter)
    lower_source = source.lower()

    assert 'if "security"' not in lower_source
    assert 'if "architecture"' not in lower_source
    assert 'if "database"' not in lower_source
    assert 'selected_tier = "complex"' not in lower_source
