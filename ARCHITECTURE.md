# Engine Architecture Specification

The orchestrator follows a hybrid intelligence, code-first architecture where deterministic analysis handles instant routing, while an optional semantic AI analyzer is reserved for high ambiguity.

```
                    USER REQUEST
                         │
                         ▼
                  FastAPI REST API
               (POST /api/orchestrate)
                         │
                         ▼
             Orchestrator Core Facade
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
Task Analyzer & Requirements       Model Registry
(Domain != Complexity)             (models.json)
        │                                 │
        ▼                                 │
Complexity Engine (16-Dim)                │
(Feature Interactions)                    │
        │                                 │
        └────────────────┬────────────────┘
                         ▼
                  Capability Matcher
                         │
                         ▼
                    Model Router
        (Hard Overrides & Soft Thresholds)
                         │
                         ▼
                  Task Decomposer
                 (DAG Task Graph)
                         │
                         ▼
                  Context Manager
                 (Worker Isolation)
                         │
                         ▼
                  Async Scheduler
               (Parallel Execution)
                         │
                         ▼
                 Verification Engine
             (Pass / Retry / Replan)
```

## Core Systems Breakdown

1. **`orchestrator.analysis`**:
   - `DeterministicAnalyzer`: Sub-10ms NLP requirement extraction.
   - `ComplexityAnalyzer`: 16-dimensional scoring engine with feature interaction bonuses (e.g. `planning x dependency`, `architecture x scale`).
2. **`orchestrator.routing`**:
   - `CapabilityMatcher`: Matrix compatibility evaluation between `TaskRequirements` and `ModelCapabilityProfile`.
   - `ModelRouter`: Policy-driven model selector generating `RoutingDecision`.
3. **`orchestrator.planning`**:
   - `TaskDecomposer`: Constructs a DAG `TaskGraph` for complex multi-component workflows while keeping simple queries as single-node graphs.
4. **`orchestrator.context`**:
   - `ContextManager`: Enforces worker isolation by packaging scoped `ContextPackage` inputs (only direct parent dependency outputs are passed).
5. **`orchestrator.execution`**:
   - `AsyncScheduler`: Executes ready DAG nodes in parallel using `asyncio`.
   - `ModelExecutor`: Provider-agnostic execution wrapper delegating to `ModelProvider` adapters.
6. **`orchestrator.verification` & `recovery`**:
   - `Verifier`: Closed-loop verification of deliverable syntax, structural specs, and constraints.
   - `Replanner` & `EscalationManager`: Model tier escalation ($M1 \rightarrow M2 \rightarrow M3$) and dynamic graph replanning upon task failure.
