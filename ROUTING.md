# Multi-Dimensional Routing & Capability Matching Algorithm

The orchestrator avoids simplistic keyword-only routing. Model tier selection is determined through multi-dimensional capability matching, hard overrides, and feature interaction effects.

---

## 1. 16 Core Complexity Dimensions

| Dimension | Description | Score Range |
| :--- | :--- | :---: |
| `reasoning_depth` | Algorithmic logic and formal proof density | 0.0 – 1.0 |
| `planning_requirement` | Multi-step roadmap & decomposition needs | 0.0 – 1.0 |
| `implementation_scope` | Code volume and component breadth | 0.0 – 1.0 |
| `dependency_complexity` | Inter-service and data dependencies | 0.0 – 1.0 |
| `architecture_complexity` | Distributed & cloud-native architecture | 0.0 – 1.0 |
| `integration_complexity` | Multi-API / database integration depth | 0.0 – 1.0 |
| `context_requirement` | Required input context window size | 0.0 – 1.0 |
| `ambiguity` | Underspecified requirements | 0.0 – 1.0 |
| `constraint_density` | Strict performance / security limits | 0.0 – 1.0 |
| `tool_requirement` | Function calling / execution tool needs | 0.0 – 1.0 |
| `statefulness` | Stateful database / session management | 0.0 – 1.0 |
| `scale_requirement` | High-frequency or distributed scale | 0.0 – 1.0 |
| `reliability_requirement` | Fault tolerance & high availability | 0.0 – 1.0 |
| `security_requirement` | Compliance, auth, and crypto constraints | 0.0 – 1.0 |
| `testing_requirement` | Test coverage & formal verification | 0.0 – 1.0 |
| `output_complexity` | Multi-file or structured schema complexity | 0.0 – 1.0 |

---

## 2. Non-Linear Feature Interactions

When multiple high-risk dimensions coincide, the engine applies non-linear interaction bonuses:

- **Planning $\times$ Dependency**: $+12$ points when planning $\ge 0.7$ and dependency $\ge 0.7$.
- **Architecture $\times$ Scale**: $+10$ points for enterprise distributed systems.
- **Reasoning $\times$ Constraints**: $+10$ points for formal mathematical proofs or security audits.
- **Implementation $\times$ Integration**: $+8$ points for multi-service software.

---

## 3. Capability Matching Matrix

`CapabilityMatcher` computes suitability between `TaskRequirements` and `ModelCapabilityProfile`:

$$\text{Suitability} = \sum w_i \cdot \left(1.0 - \max(0, R_i - C_i)\right)$$

where $R_i$ is task requirement and $C_i$ is model capability.

---

## 4. Hard Overrides

Certain critical constraints immediately trigger Model 3 escalation regardless of score:
- `security_critical == True` (PCI-DSS Level 1, HSM, zero-knowledge proofs, smart contract audits)
- `system_architecture == True` (Distributed consensus, multi-region platforms)
- `formal_proof == True` (Formal mathematical derivations, theorem proofs)
