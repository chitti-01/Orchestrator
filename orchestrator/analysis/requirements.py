from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RequirementItem(BaseModel):
    id: str                              # e.g., "R1", "R2", "R3"
    description: str                     # e.g., "Support concurrent document uploads"
    category: str = "functional"         # functional, non_functional, reliability, security, performance, scale
    criticality: str = "medium"          # critical, high, medium, low
    explicit: bool = True                # True for explicit prompt requirements, False for implicit dependencies
    source_span: Optional[str] = None     # Extract snippet from raw prompt
    dependencies: List[str] = Field(default_factory=list) # List of parent requirement IDs
    required_capabilities: List[str] = Field(default_factory=list) # e.g. ["concurrency", "architecture", "security"]
    satisfied: bool = False

    # Backwards compatibility accessor
    @property
    def req_id(self) -> str:
        return self.id

    @property
    def title(self) -> str:
        return self.description

class TaskRequirements(BaseModel):
    raw_prompt: str
    
    # 1. INTENT, DELIVERABLE, SCOPE
    intent: str = "query_info"           # explain, answer, summarize, compare, generate, implement, build, design, architect, debug, refactor, optimize, audit, prove, analyze, migrate, integrate, test
    deliverable_type: str = "text"       # natural_language_answer, explanation, code, API, architecture, database_design, system_design, algorithm, proof, report, migration_plan, test_suite
    scope: str = "single_operation"      # single_operation, single_component, multiple_components, complete_system, multi_system, platform_level
    
    # 2. CONSTRAINTS & RISK
    constraints: List[str] = Field(default_factory=list)
    actors_components: List[str] = Field(default_factory=list)
    
    # 3. TECHNOLOGY SEPARATION (Rule C)
    explicit_technologies: List[str] = Field(default_factory=list)    # Requested by user
    recommended_technologies: List[str] = Field(default_factory=list) # Presented as recommendations ONLY
    explicit_exclusions: List[str] = Field(default_factory=list)      # Prohibited assumptions ("Do not assume any specific database...")
    implicit_dependencies: List[str] = Field(default_factory=list)

    # 4. DOMAIN & ACTIONABILITY
    target_domain: str = "general"
    is_actionable: bool = False
    can_solve_directly: bool = True

    # 5. 16 CORE COMPLEXITY DIMENSIONS (0.0 to 1.0)
    reasoning_depth: float = Field(default=0.2, ge=0.0, le=1.0)
    planning_requirement: float = Field(default=0.2, ge=0.0, le=1.0)
    implementation_scope: float = Field(default=0.2, ge=0.0, le=1.0)
    dependency_complexity: float = Field(default=0.1, ge=0.0, le=1.0)
    architecture_complexity: float = Field(default=0.1, ge=0.0, le=1.0)
    integration_complexity: float = Field(default=0.1, ge=0.0, le=1.0)
    context_requirement: float = Field(default=0.2, ge=0.0, le=1.0)
    ambiguity: float = Field(default=0.2, ge=0.0, le=1.0)
    constraint_density: float = Field(default=0.2, ge=0.0, le=1.0)
    tool_requirement: float = Field(default=0.1, ge=0.0, le=1.0)
    statefulness: float = Field(default=0.1, ge=0.0, le=1.0)
    scale_requirement: float = Field(default=0.1, ge=0.0, le=1.0)
    reliability_requirement: float = Field(default=0.2, ge=0.0, le=1.0)
    security_requirement: float = Field(default=0.2, ge=0.0, le=1.0)
    testing_requirement: float = Field(default=0.1, ge=0.0, le=1.0)
    output_complexity: float = Field(default=0.2, ge=0.0, le=1.0)

    # 6. EXTRACTED REQUIREMENT OBJECTS (R1..Rn)
    extracted_requirements: List[RequirementItem] = Field(default_factory=list)

    # Metadata & Flags
    security_critical: bool = False
    system_architecture: bool = False
    formal_proof: bool = False
    multi_component: bool = False
    component_count: int = 1
    estimated_steps: int = 1
    token_estimate: int = 0
