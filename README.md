# Production-Grade Intelligent Model Orchestrator (V4 Architecture)

A standalone, production-oriented, model-agnostic AI orchestration engine designed to plug into enterprise modular monoliths.

Features deterministic sub-millisecond requirement extraction, requirement graph generation ($R_1 \dots R_n$), explicit uncertainty evaluation (`AnalysisConfidence`), multi-dimensional complexity engine with per-dimension evidence trails, general-purpose requirement clustering DAG decomposition, per-task capability-based cost-aware routing (allowing M1/M2/M3 in the same workflow), clean mock provider with zero technology hallucination, requirement coverage verification with evidence, failure analysis replanning, and a 300+ prompt benchmark suite.

---

## Core V4 Architectural Principles

1. **Rule A — Requirements Create Tasks**: Complexity is an attribute of a requirement/task, NOT the source of DAG creation. Tasks are dynamically created by clustering extracted requirement items ($R_1 \dots R_n$).
2. **Rule B — Overall Complexity $\neq$ Model Assignment**: A complex Model 3 workflow can assign Model 1, Model 2, and Model 3 to different task nodes within the same DAG based on per-task capability matching (e.g. Architecture $\rightarrow$ M3, Document Ingestion $\rightarrow$ M2, Basic Docs $\rightarrow$ M1).
3. **Rule C — No Hallucinated Technologies**: Strict enforcement against injecting unrequested technologies (Redis, PostgreSQL, Kafka, Kubernetes, AWS, etc.) when the user prompt specifies "Do not assume any specific database, cloud provider...".
4. **Rule D & E — Length & Domain $\neq$ Complexity**: Short prompts ("Build a globally distributed collaborative editor...") are recognized as HIGH complexity; long prompts ("Explain TCP 3-way handshake in 1500 words...") are recognized as LOW/MEDIUM complexity. Informational domain Q&A ("What is Kubernetes?") stays Model 1.
5. **Explicit Uncertainty Model & Fast Path (`AnalysisConfidence`)**: Tracks `overall_confidence`, `requirement_confidence`, `complexity_confidence`, `routing_confidence`, and `uncertainty_reasons`. High confidence skips AI calls; low confidence triggers optional `SemanticAIAnalyzer`.
6. **Complexity Evidence Trails**: Every complexity dimension produces a concrete evidence list (e.g. `reasoning: {score: 0.92, evidence: ["concurrent document state consistency"]}`).
7. **Requirement Coverage & Failure Analysis**: Evaluates $R_1 \dots R_n$ satisfaction (`SATISFIED`, `PARTIALLY_SATISFIED`, `UNSATISFIED`) with evidence trails and classifies failure causes (`insufficient_model_capability`, `missing_context`, `planning_error`, `verification_failure`).

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run All Tests (Unit, Planner, Adversarial, Critical Cases V3 & V4)
```bash
python -m pytest tests/
```

### 3. Run Benchmark Suite (150 Prompts)
```bash
python -m benchmarks.routing_benchmark
```

### 4. Launch FastAPI Application & Dashboard UI
```bash
python -m api.main
```
Open `http://127.0.0.1:8000/` in your browser to test prompts interactively.
